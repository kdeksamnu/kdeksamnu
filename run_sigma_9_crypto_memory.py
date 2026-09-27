#!/usr/bin/env python3

"""
CHAMBER Σ-9 // CRYPTOGRAPHIC MEMORY

Creates an append-only cryptographic transaction chain.

Σ-8:
    Contradiction → Archive

Σ-9:
    Contradiction → Archive → Cryptographic Identity
"""

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Integer,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class CryptographicTransaction(Base):
    __tablename__ = "cryptographic_ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)

    logical_state = Column(String(50), nullable=False)
    operation = Column(String(100), nullable=False)

    thermal_rate_hz = Column(Float, nullable=False)

    spectral_constant = Column(String(100), nullable=False)
    spectral_frequency_hz = Column(Float, nullable=False)

    observer_name = Column(String(100), nullable=False)

    timestamp_utc = Column(String(100), nullable=False)

    previous_hash = Column(String(64), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    transaction_hash = Column(String(64), nullable=False)

    verification_status = Column(String(50), nullable=False)


def canonical_payload(event):
    """
    Produce deterministic JSON.

    sort_keys=True and compact separators ensure that
    equivalent events generate identical payload bytes.
    """

    return json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_hex(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def build_transaction_hash(
    payload_hash,
    previous_hash,
    timestamp_utc,
):
    material = (
        f"{previous_hash}|"
        f"{payload_hash}|"
        f"{timestamp_utc}"
    )

    return sha256_hex(material)


def execute_sigma_9():

    print("=" * 72)
    print("CHAMBER Σ-9 // CRYPTOGRAPHIC MEMORY")
    print("=" * 72)

    db_url = "sqlite:///./ash_archive.db"

    engine = create_engine(
        db_url,
        echo=False,
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:

        # --------------------------------------------------------------
        # 1. Construct successor event
        # --------------------------------------------------------------

        print("\n[Σ-9.1] CONSTRUCTING SUCCESSOR EVENT")

        event = {
            "logical_state": "BOTH",
            "operation": "contradictory_observation",
            "thermal_rate_hz": 1.5,
            "spectral_constant": "Teal/Curiosity",
            "spectral_frequency_hz": 528.0,
            "observer_name": "Riot Dre'atha",
        }

        print(f"[+] Event: {event}")

        # --------------------------------------------------------------
        # 2. Canonical serialization
        # --------------------------------------------------------------

        print("\n[Σ-9.2] CANONICAL SERIALIZATION")

        payload = canonical_payload(event)

        print(f"[+] Canonical payload: {payload}")

        # --------------------------------------------------------------
        # 3. Payload hash
        # --------------------------------------------------------------

        print("\n[Σ-9.3] PAYLOAD HASH")

        payload_hash = sha256_hex(payload)

        print(f"[+] SHA-256 payload hash:")
        print(f"    {payload_hash}")

        # --------------------------------------------------------------
        # 4. Determine previous chain state
        # --------------------------------------------------------------

        print("\n[Σ-9.4] PREVIOUS HASH RESOLUTION")

        previous = (
            session.query(CryptographicTransaction)
            .order_by(CryptographicTransaction.id.desc())
            .first()
        )

        if previous is None:

            previous_hash = "0" * 64

            print("[+] No predecessor found.")
            print("[+] Establishing GENESIS HASH.")

        else:

            previous_hash = previous.transaction_hash

            print(
                f"[+] Previous transaction: #{previous.id}"
            )

            print(
                f"[+] Previous hash: {previous_hash}"
            )

        # --------------------------------------------------------------
        # 5. Timestamp
        # --------------------------------------------------------------

        timestamp_utc = datetime.now(
            timezone.utc
        ).isoformat()

        # --------------------------------------------------------------
        # 6. Transaction hash
        # --------------------------------------------------------------

        print("\n[Σ-9.5] TRANSACTION HASH")

        transaction_hash = build_transaction_hash(
            payload_hash,
            previous_hash,
            timestamp_utc,
        )

        print(
            f"[+] Transaction hash:"
        )
        print(
            f"    {transaction_hash}"
        )

        # --------------------------------------------------------------
        # 7. Append ledger record
        # --------------------------------------------------------------

        print("\n[Σ-9.6] APPEND-ONLY LEDGER WRITE")

        record = CryptographicTransaction(
            logical_state=event["logical_state"],
            operation=event["operation"],
            thermal_rate_hz=event["thermal_rate_hz"],
            spectral_constant=event["spectral_constant"],
            spectral_frequency_hz=event["spectral_frequency_hz"],
            observer_name=event["observer_name"],
            timestamp_utc=timestamp_utc,
            previous_hash=previous_hash,
            payload_hash=payload_hash,
            transaction_hash=transaction_hash,
            verification_status="PENDING",
        )

        session.add(record)
        session.commit()

        print(
            f"[+] Cryptographic transaction #{record.id} written."
        )

        # --------------------------------------------------------------
        # 8. Read-back verification
        # --------------------------------------------------------------

        print("\n[Σ-9.7] CRYPTOGRAPHIC READ-BACK")

        persisted = (
            session.query(CryptographicTransaction)
            .filter_by(id=record.id)
            .first()
        )

        assert persisted is not None

        print(
            f"[+] Retrieved transaction #{persisted.id}"
        )

        assert (
            persisted.payload_hash == payload_hash
        ), "Payload hash mismatch."

        assert (
            persisted.previous_hash == previous_hash
        ), "Previous hash mismatch."

        expected_transaction_hash = build_transaction_hash(
            persisted.payload_hash,
            persisted.previous_hash,
            persisted.timestamp_utc,
        )

        assert (
            persisted.transaction_hash
            == expected_transaction_hash
        ), "Transaction hash mismatch."

        persisted.verification_status = "VERIFIED"

        session.commit()

        print(
            "[+] Cryptographic verification COMPLETE."
        )

        # --------------------------------------------------------------
        # 9. Chain verification
        # --------------------------------------------------------------

        print("\n[Σ-9.8] CHAIN INTEGRITY CHECK")

        records = (
            session.query(CryptographicTransaction)
            .order_by(CryptographicTransaction.id.asc())
            .all()
        )

        previous_hash_check = "0" * 64

        for item in records:

            assert (
                item.previous_hash
                == previous_hash_check
            ), (
                f"Chain break at transaction #{item.id}"
            )

            recomputed = build_transaction_hash(
                item.payload_hash,
                item.previous_hash,
                item.timestamp_utc,
            )

            assert (
                item.transaction_hash
                == recomputed
            ), (
                f"Hash mismatch at transaction #{item.id}"
            )

            previous_hash_check = item.transaction_hash

            print(
                f"[+] Transaction #{item.id}: CHAIN VALID"
            )

        # --------------------------------------------------------------
        # 10. Closure
        # --------------------------------------------------------------

        print("\n" + "=" * 72)
        print("CHAMBER Σ-9 // CRYPTOGRAPHIC MEMORY CLOSED")
        print("=" * 72)

        print("[+] CANONICAL PAYLOAD : PASS")
        print("[+] PAYLOAD HASH      : PASS")
        print("[+] PREVIOUS HASH     : PASS")
        print("[+] TRANSACTION HASH  : PASS")
        print("[+] READ-BACK         : PASS")
        print("[+] CHAIN INTEGRITY   : PASS")
        print("[+] VERIFICATION      : PASS")
        print("[!] MERKLE ROOT       : NEXT STAGE")
        print("=" * 72)

    except Exception:

        session.rollback()
        raise

    finally:

        session.close()


if __name__ == "__main__":
    execute_sigma_9()
