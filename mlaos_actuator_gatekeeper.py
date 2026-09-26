import asyncio
import hmac
import hashlib
import json
import time
from typing import Dict, Any, List

# Secret key for signing Collapse Certificates
GATEKEEPER_SECRET = b"CATHEDRAL_SIGMA_12_ACTUATOR_KEY_2026"

class SimulatedGPIOPin:
    """Simulates a physical hardware GPIO pin connected to a relay or LED indicator."""
    def __init__(self, pin_number: int, label: str):
        self.pin_number = pin_number
        self.label = label
        self.state = False  # False = LOW, True = HIGH

    async def pulse(self, duration_ms: int):
        """Asynchronously toggles the pin HIGH for a specified duration, then LOW."""
        self.state = True
        print(f"  [GPIO PIN {self.pin_number:02d} // HIGH] ---> {self.label:<25} | Triggered at {time.strftime('%H:%M:%S')}.{int(time.time()*1000)%1000:03d}")
        await asyncio.sleep(duration_ms / 1000.0)
        self.state = False
        print(f"  [GPIO PIN {self.pin_number:02d} // LOW ] ---> {self.label:<25} | Reset complete")


class ActuatorGatekeeper:
    """
    Validates Collapse Certificates and orchestrates non-blocking hardware pulses
    across asynchronous GPIO relays upon state stabilization.
    """
    def __init__(self):
        # Configure simulated hardware relay board pins
        self.relays = {
            "BASALT_LATCH": SimulatedGPIOPin(18, "Basalt Latch Relay"),
            "HARMONIC_SCAR": SimulatedGPIOPin(23, "Harmonic Scar Indicator"),
            "LEX_I_CUTOUT": SimulatedGPIOPin(24, "Lex I Safety Lockout")
        }

    def generate_collapse_certificate(self, node_hash: str, epoch: int, logical_state: str) -> Dict[str, Any]:
        """Generates a cryptographically signed Collapse Certificate payload."""
        timestamp = time.time()
        message = f"{node_hash}:{epoch}:{logical_state}:{timestamp}".encode('utf-8')
        signature = hmac.new(GATEKEEPER_SECRET, message, hashlib.sha256).hexdigest()

        return {
            "version": "1.0-SIGMA12",
            "epoch": epoch,
            "node_hash": node_hash,
            "logical_state": logical_state,
            "timestamp": timestamp,
            "signature": signature
        }

    def verify_certificate(self, cert: Dict[str, Any]) -> bool:
        """Verifies HMAC signature on incoming Collapse Certificates."""
        message = f"{cert['node_hash']}:{cert['epoch']}:{cert['logical_state']}:{cert['timestamp']}".encode('utf-8')
        expected_sig = hmac.new(GATEKEEPER_SECRET, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(cert['signature'], expected_sig)

    async def process_certificate(self, cert: Dict[str, Any]):
        """Parses certificate and dispatches concurrent GPIO pulse tasks."""
        if not self.verify_certificate(cert):
            print(f"[GATEKEEPER SECURITY ALERT] Invalid certificate signature for hash {cert['node_hash'][:16]}... REJECTING!")
            return

        print(f"\n[ACTUATOR GATEKEEPER] Valid Certificate Accepted | Node: {cert['node_hash'][:16]}... | State: {cert['logical_state']}")

        tasks = []
        state = cert["logical_state"]

        if state == "SOLIDIFIED_LEX_I" or state == "PARACONSISTENT_RECONCILED":
            # Pulse Basalt Latch Relay for 120ms
            tasks.append(self.relays["BASALT_LATCH"].pulse(120))

        if "SCAR" in state or "RECONCILED" in state:
            # Pulse Harmonic Scar LED for 200ms
            tasks.append(self.relays["HARMONIC_SCAR"].pulse(200))

        if state == "LEX_I_VIOLATION_INTERCEPTED":
            # Rapid pulse Safety Cutout Relay for 50ms
            tasks.append(self.relays["LEX_I_CUTOUT"].pulse(50))

        # Execute all relay pulses asynchronously without blocking main thread
        await asyncio.gather(*tasks)


async def main():
    print("=================================================================")
    print("     CHAMBER Σ-12 // ASYNCHRONOUS HARDWARE RELAY SIMULATOR       ")
    print("=================================================================")

    gatekeeper = ActuatorGatekeeper()

    # Event 1: Reconciled Strata Collapse Certificate
    cert1 = gatekeeper.generate_collapse_certificate(
        node_hash="e81b29a40f7d312e0000000000000000",
        epoch=3,
        logical_state="PARACONSISTENT_RECONCILED"
    )

    # Event 2: Lex I Violation Intercept Event
    cert2 = gatekeeper.generate_collapse_certificate(
        node_hash="f4091a2d80e3518a0000000000000000",
        epoch=3,
        logical_state="LEX_I_VIOLATION_INTERCEPTED"
    )

    # Event 3: Final Lithic Solidification Certificate
    cert3 = gatekeeper.generate_collapse_certificate(
        node_hash="a1c9e802f34511c90000000000000000",
        epoch=3,
        logical_state="SOLIDIFIED_LEX_I"
    )

    # Dispatch events into async event loop
    print("\n--- Dispatching Event 1: Epoch 3 Reconciliation ---")
    await gatekeeper.process_certificate(cert1)

    print("\n--- Dispatching Event 2: Lex I Security Intercept ---")
    await gatekeeper.process_certificate(cert2)

    print("\n--- Dispatching Event 3: Lithic Solidification ---")
    await gatekeeper.process_certificate(cert3)

    print("\n=================================================================")
    print("                HARDWARE PULSE SIMULATION COMPLETE               ")
    print("=================================================================")


if __name__ == "__main__":
    asyncio.run(main())
