# infrastructure/database/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# --- Motores para cada base de datos ---
scan_engine = create_engine(settings.SCAN_DB_URL)
asset_engine = create_engine(settings.ASSET_DB_URL)
vuln_engine = create_engine(settings.VULN_DB_URL)
risk_engine = create_engine(settings.RISK_DB_URL)

# --- SessionMakers para cada motor ---
# Cada uno crea sesiones para su base de datos específica.
ScanSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=scan_engine)
AssetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=asset_engine)
VulnSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vuln_engine)
RiskSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=risk_engine)

# Ya no usaremos un get_db genérico. El repositorio manejará las sesiones.