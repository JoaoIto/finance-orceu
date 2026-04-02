import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.domain.entities import ScheduleType, ScheduleStatus

# Base DTOs
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# Responses
class ContactResponse(BaseSchema):
    id: uuid.UUID
    name: str
    document_number: Optional[str]
    email: Optional[str]

class CategoryResponse(BaseSchema):
    id: uuid.UUID
    name: str

class CostCenterResponse(BaseSchema):
    id: uuid.UUID
    name: str

class PaymentResponse(BaseSchema):
    id: uuid.UUID
    value_paid: Decimal
    payment_date: date
    receipt_document: Optional[str]
    created_at: datetime

class ScheduleResponse(BaseSchema):
    id: uuid.UUID
    contact_id: uuid.UUID
    category_id: uuid.UUID
    cost_center_id: uuid.UUID
    type: ScheduleType
    description: Optional[str]
    value: Decimal
    issue_date: Optional[date]
    due_date: date
    status: ScheduleStatus
    total_paid: Decimal
    payments: List[PaymentResponse] = []

# Requests / Commands
class CreateCategoryRequest(BaseSchema):
    name: str

class CreateCostCenterRequest(BaseSchema):
    name: str

class CreateContactRequest(BaseSchema):
    name: str
    document_number: Optional[str] = None
    email: Optional[str] = None

class CreateScheduleRequest(BaseSchema):
    contact_id: uuid.UUID = Field(..., description="ID do Contato associado a obrigação.")
    category_id: uuid.UUID = Field(..., description="ID da Categoria (Ex: Materiais, Folha)")
    cost_center_id: uuid.UUID
    description: Optional[str] = None
    value: Decimal = Field(..., gt=0, description="Amount must be strictly positive")
    issue_date: Optional[date] = None
    due_date: date
    
class CreatePaymentRequest(BaseSchema):
    value_paid: Decimal = Field(..., gt=0, description="Amount paid must be strictly positive", examples=[500.00])
    payment_date: date = Field(..., description="Data real do recebimento/pagamento.", examples=["2026-04-02"])
    receipt_document: Optional[str] = Field(None, description="Número de NSU, Boleto ou Cheque.", examples=["NSU-12345"])
