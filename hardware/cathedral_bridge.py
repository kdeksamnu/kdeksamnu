#!/usr/bin/env python3
"""
Cathedral Engine: Raspberry Pi Cortex Bridge
Purpose: Coordinates high-level state, listens for Metamorphic Squeeze events,
         and dispatches Pyragas actuation commands to the Arduino.
"""

import serial
import time
import threading

# Configuration
SERIAL_PORT = '/dev/ttyACM0'  # Adjust for your Arduino (e.g., /dev/ttyUSB0)
BAUD_RATE = 115200

class CathedralBridge:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = False
        self.telemetry_thread = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2) # Wait for Arduino reset
            print("[M8 CORTEX] Connected to Pyragas Actuator.")
            self.running = True
            self.telemetry_thread = threading.Thread(target=self._read_telemetry, daemon=True)
            self.telemetry_thread.start()
            return True
        except serial.SerialException as e:
            print(f"[M8 CORTEX ERROR] Failed to connect: {e}")
            return False

    def trigger_squeeze(self):
        """Dispatches the command to engage the Pyragas loop."""
        if self.ser and self.ser.is_open:
            print("[M8 CORTEX] Dispatching METAMORPHIC SQUEEZE command...")
            self.ser.write(b"ACTUATE\n")
            self.ser.flush()

    def halt_actuation(self):
        """Dispatches the command to disengage and lock."""
        if self.ser and self.ser.is_open:
            print("[M8 CORTEX] Dispatching HALT command. Locking at Magic Angle.")
            self.ser.write(b"HALT\n")
            self.ser.flush()

    def _read_telemetry(self):
        """Background thread to read and parse Arduino telemetry."""
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line.startswith("TELEMETRY"):
                        # Parse: TELEMETRY|Omega:0.0123|Torque:-0.0045
                        parts = line.split('|')
                        if len(parts) == 3:
                            omega = parts[1].split(':')[1]
                            torque = parts[2].split(':')[1]
                            print(f"  [Telemetry] Ω: {omega} rad/s | τ: {torque} N·m")
            except Exception as e:
                print(f"[M8 CORTEX ERROR] Telemetry read failed: {e}")
                break

    def close(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        print("[M8 CORTEX] Bridge closed.")

if __name__ == "__main__":
    print("==================================================================")
    print(" CATHEDRAL ENGINE: M8 HARDWARE BRIDGE INITIALIZED")
    print(" Press 'S' to trigger Metamorphic Squeeze, 'H' to Halt, 'Q' to Quit.")
    print("==================================================================")
    
    bridge = CathedralBridge(SERIAL_PORT, BAUD_RATE)
    if bridge.connect():
        try:
            while True:
                cmd = input("> ").strip().upper()
                if cmd == 'S':
                    bridge.trigger_squeeze()
                elif cmd == 'H':
                    bridge.halt_actuation()
                elif cmd == 'Q':
                    break
        except KeyboardInterrupt:
            print("\n[M8 CORTEX] Interrupt received.")
        finally:
            bridge.close()
