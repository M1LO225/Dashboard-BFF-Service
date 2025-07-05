from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

# These are Pydantic models, not domain entities in the DDD sense.
# They define the structure of the data this service works with.

class RiskDetail(BaseModel):
    id: uuid.UUID
    cve_id: str
    cvss_score: float
    risk_score: float # NR

class AssetDetail(BaseModel):
    id: uuid.UUID
    value: str
    sca_score: Optional[float]
    risks: List[RiskDetail] = []

class DashboardData(BaseModel):
    scan_id: uuid.UUID
    domain_name: str
    status: str
    requested_at: datetime
    total_risk_score: Optional[float] = 0.0 # An aggregated score for the whole scan
    assets: List[AssetDetail] = []