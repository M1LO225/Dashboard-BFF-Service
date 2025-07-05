from abc import ABC, abstractmethod
from typing import Optional
import uuid
from domain.entities.dashboard import DashboardData

class IDashboardRepository(ABC):
    """Abstract interface for reading aggregated dashboard data."""

    @abstractmethod
    def get_dashboard_by_scan_id(self, scan_id: uuid.UUID) -> Optional[DashboardData]:
        pass