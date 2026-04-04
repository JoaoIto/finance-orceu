import uuid
from typing import List, Optional, Tuple
from datetime import date

from app.domain.entities import Schedule, Category, CostCenter, Contact
from app.domain.repositories import (
    ScheduleRepository, CategoryRepository, 
    CostCenterRepository, ContactRepository
)

class QueryHandler:
    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        category_repo: CategoryRepository = None,
        cost_center_repo: CostCenterRepository = None,
        contact_repo: ContactRepository = None
    ):
        self.schedule_repo = schedule_repo
        self.category_repo = category_repo
        self.cost_center_repo = cost_center_repo
        self.contact_repo = contact_repo

    def get_categories(self, org_id: uuid.UUID) -> List[Category]:
        return self.category_repo.get_all(org_id)

    def get_cost_centers(self, org_id: uuid.UUID) -> List[CostCenter]:
        return self.cost_center_repo.get_all(org_id)

    def get_contacts(self, org_id: uuid.UUID) -> List[Contact]:
        return self.contact_repo.get_all(org_id)

    def get_schedules(
        self, 
        org_id: uuid.UUID, 
        type: Optional[str] = None,
        status: Optional[str] = None,
        due_date_from: Optional[date] = None,
        due_date_to: Optional[date] = None,
        category_id: Optional[uuid.UUID] = None,
        cost_center_id: Optional[uuid.UUID] = None,
        contact_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        top: int = 50,
        order_by: str = "dueDate"
    ) -> Tuple[int, List[Schedule]]:
        return self.schedule_repo.get_all(
            org_id, type, status, due_date_from, due_date_to,
            category_id, cost_center_id, contact_id, skip, top, order_by
        )
        
    def get_schedule(self, org_id: uuid.UUID, schedule_id: uuid.UUID) -> Optional[Schedule]:
        return self.schedule_repo.get_by_id(org_id, schedule_id)
        
    def get_schedule_summary(
        self, 
        org_id: uuid.UUID,
        due_date_from: Optional[date] = None,
        due_date_to: Optional[date] = None
    ) -> dict:
        return self.schedule_repo.get_summary(org_id, due_date_from, due_date_to)
