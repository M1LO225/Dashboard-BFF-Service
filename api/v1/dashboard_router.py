import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.v1.security import get_current_user_id
from domain.entities.dashboard import DashboardData # Import the domain model for response
from application.use_cases.get_dashboard_data import GetDashboardDataUseCase
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.database.connection import get_db # Import the database dependency
from infrastructure.repositories.postgres_dashboard_repository import PostgresDashboardRepository

router = APIRouter()

@router.get("/{scan_id}", response_model=DashboardData, summary="Get Aggregated Dashboard Data for a Scan")
def get_dashboard_data(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db), # Inject a database session
    user_id: uuid.UUID = Depends(get_current_user_id) # Ensure authentication
):
    """
    Retrieves the comprehensive aggregated dashboard data for a specific scan ID.
    This endpoint is protected by JWT authentication.
    
    - **scan_id**: The unique identifier of the scan to retrieve data for.
    - **user_id**: The ID of the authenticated user (obtained from JWT).
    
    Returns all relevant information about the scan, including assets, vulnerabilities,
    and calculated risks, in a single structured response.
    """
    # Dependency Injection: Instantiate the concrete implementations
    # and pass them to the use case.
    repo = PostgresDashboardRepository(db) # Repository needs a DB session
    cache = RedisCache() # Cache client
    use_case = GetDashboardDataUseCase(repo, cache)

    # Execute the use case to fetch the dashboard data
    dashboard = use_case.execute(scan_id=scan_id, user_id=user_id)
    
    if not dashboard:
        # If no dashboard data is found (e.g., scan_id does not exist or user lacks permission)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found or you do not have permission to view it."
        )

    # Return the aggregated data, FastAPI will serialize it to JSON
    return dashboard