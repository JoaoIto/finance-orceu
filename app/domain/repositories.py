from abc import ABC, abstractmethod
import uuid
from typing import List, Optional

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
    def get_all(self, org_id: uuid.UUID, status: Optional[str] = None) -> List[Schedule]:
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
