# infrastructure/repositories/postgres_dashboard_repository.py

import uuid
from typing import Optional
from domain.entities.dashboard import DashboardData, AssetDetail, RiskDetail
from domain.repositories.dashboard_repository import IDashboardRepository
from infrastructure.database.models import ScanDB, AssetDB, VulnerabilityDB, RiskDB
# Importamos todos los session makers
from infrastructure.database.connection import (
    ScanSessionLocal,
    AssetSessionLocal,
    VulnSessionLocal,
    RiskSessionLocal,
)

class PostgresDashboardRepository(IDashboardRepository):
    # Ya no recibe una sesión en el constructor
    def __init__(self):
        pass

    def get_dashboard_by_scan_id(self, scan_id: uuid.UUID) -> Optional[DashboardData]:
        # Usamos context managers ('with') para cada sesión de base de datos
        
        # 1. Get the base scan info from scan_db
        with ScanSessionLocal() as db_scan:
            scan = db_scan.query(ScanDB).filter(ScanDB.id == scan_id).first()
            if not scan:
                return None
            
            dashboard = DashboardData(
                scan_id=scan.id,
                domain_name=scan.domain_name,
                status=scan.status.value,
                requested_at=scan.requested_at
            )

        # 2. Get all assets for this scan from asset_db
        with AssetSessionLocal() as db_asset:
            assets = db_asset.query(AssetDB).filter(AssetDB.scan_id == scan_id).all()
            asset_map = {
                asset.id: AssetDetail(id=asset.id, value=asset.value, sca_score=asset.sca) 
                for asset in assets
            }

        # 3. Get all risks and vulnerabilities from their respective DBs
        # Esta es la consulta más compleja que une datos de risk_db y vuln_db
        with RiskSessionLocal() as db_risk, VulnSessionLocal() as db_vuln:
            # Primero obtenemos todos los riesgos del scan
            risks_query = db_risk.query(RiskDB).filter(RiskDB.scan_id == scan_id).all()
            if not risks_query:
                dashboard.assets = list(asset_map.values())
                return dashboard
            
            vulnerability_ids = [risk.vulnerability_id for risk in risks_query]
            
            # Ahora, con los IDs de las vulnerabilidades, las buscamos en su DB
            vulnerabilities = db_vuln.query(VulnerabilityDB).filter(VulnerabilityDB.id.in_(vulnerability_ids)).all()
            vuln_map = {v.id: v for v in vulnerabilities}

        total_risk = 0.0
        for risk in risks_query:
            total_risk += risk.nr_score
            vulnerability = vuln_map.get(risk.vulnerability_id)
            
            if risk.asset_id in asset_map and vulnerability:
                risk_detail = RiskDetail(
                    id=risk.id,
                    cve_id=vulnerability.cve_id,
                    cvss_score=vulnerability.cvss_score,
                    risk_score=risk.nr_score
                )
                asset_map[risk.asset_id].risks.append(risk_detail)

        dashboard.assets = list(asset_map.values())
        dashboard.total_risk_score = round(total_risk / len(risks_query), 2)

        return dashboard