import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class ScheduleType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class ScheduleStatus(str, Enum):
    OPEN = "OPEN"
    PAID = "PAID"
    OVERDUE = "OVERDUE"

class DomainEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Organization(DomainEntity):
    name: str
    tax_id: Optional[str] = None

class Contact(DomainEntity):
    organization_id: uuid.UUID
    name: str
    document_number: Optional[str] = None
    email: Optional[str] = None

class Category(DomainEntity):
    organization_id: uuid.UUID
    name: str

class CostCenter(DomainEntity):
    organization_id: uuid.UUID
    name: str

class Payment(DomainEntity):
    organization_id: uuid.UUID
    schedule_id: uuid.UUID
    value_paid: Decimal
    payment_date: date
    receipt_document: Optional[str] = None

class Schedule(DomainEntity):
    organization_id: uuid.UUID
    contact_id: uuid.UUID
    category_id: uuid.UUID
    cost_center_id: uuid.UUID
    type: ScheduleType
    description: Optional[str] = None
    value: Decimal
    issue_date: Optional[date] = None
    due_date: date
    
    # Domain aggregated property logic (simulated for business rules)
    payments: List[Payment] = Field(default_factory=list)

    @property
    def total_paid(self) -> Decimal:
        return sum(p.value_paid for p in self.payments)

    @property
    def status(self) -> ScheduleStatus:
        if self.total_paid >= self.value:
            return ScheduleStatus.PAID
        
        if date.today() > self.due_date:
            return ScheduleStatus.OVERDUE
            
        return ScheduleStatus.OPEN

    def can_receive_payment(self, amount: Decimal) -> bool:
        """
        Business Rule: Impeditivo de Estouro Transacional.
        """
        return (self.total_paid + amount) <= self.value
