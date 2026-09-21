"""The Ash Archive: Cryptographic Merkle DAG, Somatic Observers, and Ideological Collectives."""
import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, String, Uuid, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class LogicStateEnum(str, enum.Enum):
    TRUE = "True"
    FALSE = "False"
    BOTH = "Both"
    NEITHER = "Neither"

class SpectralConstantEnum(str, enum.Enum):
    GOLD_JOY = "gold_joy"
    TEAL_CURIOSITY = "teal_curiosity"
    BLUE_SORROW = "blue_sorrow"
    RED_ANGER = "red_anger"
    VIOLET_FEAR = "violet_fear"
    EMERALD_LOVE = "emerald_love"
    BRONZE_OBSIDIAN_NULL = "bronze_obsidian_null"

class Faction(Base):
    __tablename__ = "factions"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    designation = Column(String(64), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    observers = relationship("ObserverNode", back_populates="faction_ref", cascade="all, delete-orphan")

class ObserverNode(Base):
    """The somatic anchor. Treated strictly as a materialized read-model of the event lineage."""
    __tablename__ = "observer_nodes"

    observer_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    designation = Column(String(64), nullable=False, unique=True, index=True)
    faction = Column(String(64), nullable=False, default="unaligned")
    
    faction_id = Column(Uuid, ForeignKey("factions.id"), nullable=True, index=True)
    faction_ref = relationship("Faction", back_populates="observers")
    
    # Materialized State Invariants
    ego_density = Column(Float, nullable=False, default=1.0)
    somatic_integrity = Column(Float, nullable=False, default=1.000)
    
    # The Dual-Metric Schema & Legacy Compatibility
    harmonic_scars_total = Column(Integer, nullable=False, default=0) # Legacy scalar for immediate service compatibility
    lifetime_harmonic_scars = Column(Integer, nullable=False, default=0)
    active_harmonic_scars = Column(Integer, nullable=False, default=0)
    
    quarantine_events_total = Column(Integer, nullable=False, default=0)
    lineage_intact = Column(Boolean, nullable=False, default=True, server_default="1")
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    events = relationship("SpectralEvent", back_populates="observer", cascade="all, delete-orphan")

class SpectralEvent(Base):
    """Immutable ledger leaf in the Ash Archive Merkle chain."""
    __tablename__ = "spectral_events"

    event_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    observer_id = Column(Uuid, ForeignKey("observer_nodes.observer_id"), nullable=False, index=True)
    observer = relationship("ObserverNode", back_populates="events")
    
    primary_constant = Column(Enum(SpectralConstantEnum), nullable=False)
    secondary_constant = Column(Enum(SpectralConstantEnum), nullable=True)
    magnitude = Column(Float, nullable=False)
    harmonic_phase = Column(Float, nullable=False, default=0.0)
    topological_continuity = Column(Boolean, nullable=False, default=True)
    micro_fracture_detected = Column(Boolean, nullable=False, default=False)
    harmonic_scar_applied = Column(Boolean, nullable=False, default=False)
    logic_state = Column(Enum(LogicStateEnum), nullable=False)
    parent_hash = Column(String(64), nullable=False)
    state_hash = Column(String(64), nullable=False, unique=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Reconciliation Fields
    is_reconciliation = Column(Boolean, nullable=False, default=False, server_default="0")
    reconciliation_magnitude = Column(Float, nullable=True)
    scars_to_neutralize = Column(Integer, nullable=False, default=0)
