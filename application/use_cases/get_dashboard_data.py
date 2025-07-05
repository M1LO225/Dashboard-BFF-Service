import logging
import uuid
from typing import Optional

from domain.entities.dashboard import DashboardData
from domain.repositories.dashboard_repository import IDashboardRepository
from infrastructure.cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)

class GetDashboardDataUseCase:
    def __init__(self, dashboard_repo: IDashboardRepository, cache: RedisCache):
        self.dashboard_repo = dashboard_repo
        self.cache = cache

    def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID) -> Optional[DashboardData]:
        # The user_id would be used here to verify ownership of the scan
        
        cache_key = f"dashboard:{scan_id}"
        
        # 1. Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        # 2. If miss, go to the database
        logger.info(f"Fetching dashboard data from DB for scan_id: {scan_id}")
        dashboard_data = self.dashboard_repo.get_dashboard_by_scan_id(scan_id)

        # 3. If data is found, store it in the cache before returning
        if dashboard_data:
            self.cache.set(cache_key, dashboard_data)
        
        return dashboard_data