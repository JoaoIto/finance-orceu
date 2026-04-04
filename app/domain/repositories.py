from abc import ABC, abstractmethod
import uuid
from typing import List, Optional, Tuple
from datetime import date

from app.domain.entities import Organization, Contact, Category, CostCenter, Schedule, Payment

class OrganizationRepository(ABC):
    @abstractmethod
    def get_by_id(self, org_id: uuid.UUID) -> Optional[Organization]:
        pass

class ContactRepository(ABC):
    @abstractmethod
    def create(self, contact: Contact) -> Contact:
        pass
    
    @abstractmethod
    def get_all(self, org_id: uuid.UUID) -> List[Contact]:
        pass

class CategoryRepository(ABC):
    @abstractmethod
    def create(self, category: Category) -> Category:
        pass

    @abstractmethod
    def get_all(self, org_id: uuid.UUID) -> List[Category]:
        pass

class CostCenterRepository(ABC):
    @abstractmethod
    def create(self, cost_center: CostCenter) -> CostCenter:
        pass

    @abstractmethod
    def get_all(self, org_id: uuid.UUID) -> List[CostCenter]:
        pass

class ScheduleRepository(ABC):
    @abstractmethod
    def create(self, schedule: Schedule) -> Schedule:
        pass
    
    @abstractmethod
    def get_by_id(self, org_id: uuid.UUID, schedule_id: uuid.UUID) -> Optional[Schedule]:
        pass

    @abstractmethod
    def get_all(
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
    ) -> tuple[int, List[Schedule]]:
        pass
        
    @abstractmethod
    def get_summary(
        self, 
        org_id: uuid.UUID,
        due_date_from: Optional[date] = None,
        due_date_to: Optional[date] = None
    ) -> dict:
        pass
        
    @abstractmethod
    def cancel(self, org_id: uuid.UUID, schedule_id: uuid.UUID) -> bool:
        pass

class PaymentRepository(ABC):
    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        pass
        
    @abstractmethod
    def get_by_schedule_id(self, org_id: uuid.UUID, schedule_id: uuid.UUID) -> List[Payment]:
        pass
