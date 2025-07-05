import uuid
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Reusing the models from domain.entities.dashboard as they are already presentation-ready.
# This avoids duplication and ensures consistency between the internal aggregated data
# and the external API response.

# --- Response Schemas ---

class RiskDetail(BaseModel):
    """Schema for a single risk detail within an asset."""
    id: uuid.UUID
    cve_id: str
    cvss_score: float
    risk_score: float = Field(..., alias="nr_score") # Alias for NR score

    class Config:
        from_attributes = True
        populate_by_name = True # Allow mapping by alias

class AssetDetail(BaseModel):
    """Schema for a single asset with its valuation and associated risks."""
    id: uuid.UUID
    value: str
    asset_type: str # Added asset_type for more context
    sca_score: Optional[float] = None
    risks: List[RiskDetail] = []

    class Config:
        from_attributes = True

class DashboardData(BaseModel):
    """Comprehensive schema for the entire dashboard view."""
    scan_id: uuid.UUID
    domain_name: str
    status: str
    requested_at: datetime
    total_risk_score: Optional[float] = Field(0.0, description="Average NR score for the scan")
    assets: List[AssetDetail] = []

    class Config:
        from_attributes = True