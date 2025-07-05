from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from typing import Optional

from domain.entities.dashboard import DashboardData, AssetDetail, RiskDetail
from domain.repositories.dashboard_repository import IDashboardRepository
# You would need to import all DB models here
from infrastructure.database.models import ScanDB, AssetDB, VulnerabilityDB, RiskDB

class PostgresDashboardRepository(IDashboardRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_dashboard_by_scan_id(self, scan_id: uuid.UUID) -> Optional[DashboardData]:
        # This is a complex query that joins all the data together.
        # This is the primary value of the BFF - encapsulating this complexity.
        
        # 1. Get the base scan info
        scan = self.db.query(ScanDB).filter(ScanDB.id == scan_id).first()
        if not scan:
            return None
            
        dashboard = DashboardData(
            scan_id=scan.id,
            domain_name=scan.domain_name,
            status=scan.status.value,
            requested_at=scan.requested_at
        )

        # 2. Get all assets for this scan
        assets = self.db.query(AssetDB).filter(AssetDB.scan_id == scan_id).all()
        asset_map = {asset.id: AssetDetail(id=asset.id, value=asset.value, sca_score=asset.sca) for asset in assets}

        # 3. Get all risks and group them by asset
        risks = (self.db.query(RiskDB, VulnerabilityDB.cve_id, VulnerabilityDB.cvss_score)
                 .join(VulnerabilityDB, RiskDB.vulnerability_id == VulnerabilityDB.id)
                 .filter(RiskDB.scan_id == scan_id)
                 .all())
        
        total_risk = 0.0
        for risk, cve_id, cvss_score in risks:
            total_risk += risk.nr_score
            if risk.asset_id in asset_map:
                risk_detail = RiskDetail(
                    id=risk.id,
                    cve_id=cve_id,
                    cvss_score=cvss_score,
                    risk_score=risk.nr_score
                )
                asset_map[risk.asset_id].risks.append(risk_detail)

        dashboard.assets = list(asset_map.values())
        if risks:
            dashboard.total_risk_score = round(total_risk / len(risks), 2)

        return dashboard