from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
from typing import Generator

# Create engines for each database
# In a production environment, these would likely be separate database instances
# For simplicity in this demo, they might point to the same host/port/user,
# but connect to different database names.

engine_scan = create_engine(settings.SCAN_DB_URL)
engine_asset = create_engine(settings.ASSET_DB_URL)
engine_vuln = create_engine(settings.VULN_DB_URL)
engine_risk = create_engine(settings.RISK_DB_URL)

# Create SessionLocal classes for each database
ScanSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_scan)
AssetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_asset)
VulnSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_vuln)
RiskSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_risk)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session for the Dashboard BFF.
    This session will be used for queries that might join across tables
    from different conceptual databases.
    
    NOTE: For the Dashboard BFF, a single session *might* not be enough if
    your SQLAlchemy setup truly uses separate connection pools/engines
    for each 'logical' database (scan, asset, vuln, risk).
    
    A more robust approach for a BFF reading from multiple *distinct* databases
    would be to inject separate sessions for each repository, or ensure
    that the PostgresDashboardRepository handles connections via its own
    logic using the distinct engines/sessions.
    
    For a simplified setup where all 'dbs' point to the same PostgreSQL instance
    with different schema/tables, a single session might work for ORM joins.
    
    For this example, we provide a session that can be used. The
    PostgresDashboardRepository's queries are written to use its own
    session for clarity. If you use a single DB_URL for all, then this
    `get_db` could indeed provide the unified session.
    """
    db = None
    try:
        # In a multi-database read scenario, you might either:
        # 1. Have a single read-replica database that aggregates all data.
        #    In this case, only one engine/session (e.g., for SCAN_DB_URL) is needed here.
        # 2. Manage separate sessions within the repository itself,
        #    passing the appropriate engine/sessionmaker for each distinct DB access.
        
        # For simplicity and given the `get_dashboard_by_scan_id` logic,
        # we'll use a session from one of the engines, assuming either
        # a unified read-replica or that the repository handles multi-engine
        # queries internally.
        # Let's use the scan_db session as the primary FastAPI dependency hook.
        db = ScanSessionLocal() 
        yield db
    finally:
        if db:
            db.close()

# For the PostgresDashboardRepository, it will receive the session from `get_db`
# and perform the necessary joins based on the `models.py` relationships.
# If truly separate DBs, the repository would need to manage multiple
# SessionLocal instances or a custom ORM query setup that spans engines.