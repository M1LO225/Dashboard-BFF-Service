# api/v1/dashboard_router.py

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from api.v1.security import get_current_user_id
# Cambia el import de la respuesta si es necesario, asegúrate que el modelo Pydantic sea el correcto
from domain.entities.dashboard import DashboardData 
from application.use_cases.get_dashboard_data import GetDashboardDataUseCase
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.repositories.postgres_dashboard_repository import PostgresDashboardRepository

router = APIRouter()

@router.get("/{scan_id}", response_model=DashboardData)
def get_dashboard_data(
    scan_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Retrieves the aggregated dashboard data for a specific scan.
    """
    try:
        # La inyección de dependencias ahora se hace aquí directamente
        repo = PostgresDashboardRepository()
        cache = RedisCache()
        use_case = GetDashboardDataUseCase(repo, cache)

        dashboard = use_case.execute(scan_id=scan_id, user_id=user_id)
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Scan not found or you do not have permission to view it."
            )

        return dashboard
    except Exception as e:
        # Captura cualquier otra excepción para evitar que el servidor se caiga
        # y devuelve un error 500 genérico. Los detalles se verán en los logs.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e}"
        )