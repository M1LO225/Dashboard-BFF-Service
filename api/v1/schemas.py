from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

class RiskDetailResponse(BaseModel):
    id: uuid.UUID
    cve_id: str
    cvss_score: float
    risk_score: float

    class Config:
        from_attributes = True

class AssetDetailResponse(BaseModel):
    id: uuid.UUID
    value: str
    sca_score: Optional[float] = None
    risks: List[RiskDetailResponse] = []

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    scan_id: uuid.UUID
    domain_name: str
    status: str
    requested_at: datetime
    total_risk_score: Optional[float] = 0.0
    assets: List[AssetDetailResponse] = []

    class Config:
        from_attributes = True