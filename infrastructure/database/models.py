import uuid
import enum
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

# A single Base for all read-only models in this service
ReadOnlyBase = declarative_base()

# --- Enums (mirrored from other services) ---
class ScanStatusEnum(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AssetTypeEnum(enum.Enum):
    SUBDOMAIN = "SUBDOMAIN"
    IP_ADDRESS = "IP_ADDRESS"
    SERVICE = "SERVICE"
    WEBSITE = "WEBSITE"

class VulnerabilityImpactEnum(enum.Enum):
    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"


# --- Table Declarations ---

class ScanDB(ReadOnlyBase):
    """Read-only declaration of the 'scans' table."""
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    domain_name = Column(String, nullable=False)
    status = Column(SQLAlchemyEnum(ScanStatusEnum), nullable=False)
    requested_at = Column(DateTime, nullable=False)
    acceptable_loss = Column(Float, nullable=False) # Added for completeness


class AssetDB(ReadOnlyBase):
    """Read-only declaration of the 'assets' table."""
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True)
    scan_id = Column(UUID(as_uuid=True), nullable=False)
    asset_type = Column(SQLAlchemyEnum(AssetTypeEnum), nullable=False)
    value = Column(String, nullable=False)
    discovered_at = Column(DateTime, nullable=False)
    sca = Column(Float, nullable=True)
    sca_c = Column(Float, nullable=True)
    sca_i = Column(Float, nullable=True)
    sca_d = Column(Float, nullable=True)


class VulnerabilityDB(ReadOnlyBase):
    """Read-only declaration of the 'vulnerabilities' table."""
    __tablename__ = "vulnerabilities"

    id = Column(UUID(as_uuid=True), primary_key=True)
    asset_id = Column(UUID(as_uuid=True), nullable=False) 
    cve_id = Column(String, nullable=False)
    description = Column(String, nullable=False)
    cvss_score = Column(Float, nullable=False)
    confidentiality_impact = Column(SQLAlchemyEnum(VulnerabilityImpactEnum), nullable=False)
    integrity_impact = Column(SQLAlchemyEnum(VulnerabilityImpactEnum), nullable=False)
    availability_impact = Column(SQLAlchemyEnum(VulnerabilityImpactEnum), nullable=False)


class RiskDB(ReadOnlyBase):
    """Read-only declaration of the 'risks' table."""
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True)
    scan_id = Column(UUID(as_uuid=True), nullable=False)
    asset_id = Column(UUID(as_uuid=True), nullable=False)
    vulnerability_id = Column(UUID(as_uuid=True), nullable=False)
    ic_score = Column(Float, nullable=False)
    pc_score = Column(Float, nullable=False)
    nr_score = Column(Float, nullable=False)