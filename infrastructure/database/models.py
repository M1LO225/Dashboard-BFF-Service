import uuid
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base for all ORM models in this service.
# Note: This Base is for *reading* from potentially different databases.
# In a real-world scenario with separate DBs, you'd configure engines/sessions
# for each, but the models themselves can be defined once if schemas match.
Base = declarative_base()

# --- Enums (re-defined or imported to ensure consistency) ---
# It's best practice to have these enums defined in a shared library
# or ensure they are identical across all services that use them.
import enum

class ScanStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AssetType(str, enum.Enum):
    SUBDOMAIN = "SUBDOMAIN"
    IP_ADDRESS = "IP_ADDRESS"
    SERVICE = "SERVICE"
    WEBSITE = "WEBSITE"

class VulnerabilityImpact(str, enum.Enum):
    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"

# --- ORM Models for reading from other services' databases ---

class ScanDB(Base):
    """ORM model for the 'scans' table (from Scan Orchestrator Service)."""
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    domain_name = Column(String, nullable=False)
    acceptable_loss = Column(Float, nullable=False)
    status = Column(Enum(ScanStatus), nullable=False)
    requested_at = Column(DateTime, nullable=False)

    # Relationship to assets (optional, but good for joins)
    assets = relationship("AssetDB", back_populates="scan")

class AssetDB(Base):
    """ORM model for the 'assets' table (from Asset Discovery/Valuation Services)."""
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    value = Column(String, nullable=False)
    discovered_at = Column(DateTime, nullable=False)

    sca = Column(Float, nullable=True)
    sca_c = Column(Float, nullable=True)
    sca_i = Column(Float, nullable=True)
    sca_d = Column(Float, nullable=True)

    # Relationships
    scan = relationship("ScanDB", back_populates="assets")
    vulnerabilities = relationship("VulnerabilityDB", back_populates="asset")

class VulnerabilityDB(Base):
    """ORM model for the 'vulnerabilities' table (from Vulnerability Scanner Service)."""
    __tablename__ = "vulnerabilities"

    id = Column(UUID(as_uuid=True), primary_key=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    cve_id = Column(String, nullable=False)
    description = Column(String, nullable=False)
    cvss_score = Column(Float, nullable=False)
    
    confidentiality_impact = Column(Enum(VulnerabilityImpact), nullable=False)
    integrity_impact = Column(Enum(VulnerabilityImpact), nullable=False)
    availability_impact = Column(Enum(VulnerabilityImpact), nullable=False)

    # Relationships
    asset = relationship("AssetDB", back_populates="vulnerabilities")
    risks = relationship("RiskDB", back_populates="vulnerability")

class RiskDB(Base):
    """ORM model for the 'risks' table (from Risk Calculation Service)."""
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False) # Link to scan for direct access
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    vulnerability_id = Column(UUID(as_uuid=True), ForeignKey("vulnerabilities.id"), nullable=False)
    
    ic_score = Column(Float, nullable=False)
    pc_score = Column(Float, nullable=False)
    nr_score = Column(Float, nullable=False)

    # Relationships
    scan_rel = relationship("ScanDB") # No back_populates needed if not used from ScanDB
    asset_rel = relationship("AssetDB")
    vulnerability = relationship("VulnerabilityDB", back_populates="risks")