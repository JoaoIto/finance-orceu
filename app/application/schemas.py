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
    id: uuid.UUID = Field(..., description="ID Único do Contato", examples=["c95d3e02-4fc8-4228-b223-b1d7d0de04f0"])
    name: str = Field(..., examples=["Fornecedor de Argamassa S.A."])
    document_number: Optional[str] = Field(None, examples=["12345678000199"])
    email: Optional[str] = Field(None, examples=["contato@fornecedor.com.br"])

class CategoryResponse(BaseSchema):
    id: uuid.UUID = Field(..., examples=["a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6"])
    name: str = Field(..., examples=["Materiais de Construção"])

class CostCenterResponse(BaseSchema):
    id: uuid.UUID = Field(..., examples=["f1e2d3c4-b5a6-9f8e-7d6c-5b4a3f2e1d0c"])
    name: str = Field(..., examples=["Obra Residencial - Torre A"])

class PaymentResponse(BaseSchema):
    id: uuid.UUID = Field(..., examples=["e95d3e02-4fc8-4228-b223-b1d7d0de04f0"])
    value_paid: Decimal = Field(..., examples=[500.00])
    payment_date: date = Field(..., examples=["2026-04-02"])
    receipt_document: Optional[str] = Field(None, examples=["REC-998877"])
    created_at: datetime = Field(..., examples=["2026-04-02T10:00:00Z"])

class ScheduleResponse(BaseSchema):
    id: uuid.UUID = Field(..., examples=["b84d3e02-12c8-4228-b223-f1d7d0de04ab"])
    contact_id: uuid.UUID = Field(..., examples=["c95d3e02-4fc8-4228-b223-b1d7d0de04f0"])
    category_id: uuid.UUID = Field(..., examples=["a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6"])
    cost_center_id: uuid.UUID = Field(..., examples=["f1e2d3c4-b5a6-9f8e-7d6c-5b4a3f2e1d0c"])
    type: ScheduleType = Field(..., examples=["DEBIT"])
    description: Optional[str] = Field(None, examples=["Compra de argamassa 20kg"])
    value: Decimal = Field(..., examples=[1500.00])
    issue_date: Optional[date] = Field(None, examples=["2026-03-01"])
    due_date: date = Field(..., examples=["2026-04-10"])
    status: ScheduleStatus = Field(..., examples=["OPEN"])
    total_paid: Decimal = Field(..., examples=[0.00])
    payments: List[PaymentResponse] = Field(default_factory=list)

class SchedulePaginatedResponse(BaseSchema):
    total: int
    skip: int
    top: int
    items: List[ScheduleResponse]

class SummaryResponse(BaseSchema):
    due_date_from: Optional[date] = Field(None, description="Início do Período", examples=["2026-04-01"])
    due_date_to: Optional[date] = Field(None, description="Fim do Período", examples=["2026-04-30"])
    total_debit: Decimal = Field(..., examples=[2500.00])
    total_credit: Decimal = Field(..., examples=[6000.00])
    balance: Decimal = Field(..., examples=[3500.00])

# Requests / Commands
class CreateCategoryRequest(BaseSchema):
    name: str = Field(..., examples=["Materiais Elétricos"])

class CreateCostCenterRequest(BaseSchema):
    name: str = Field(..., examples=["Reforma Escritório Central"])

class CreateContactRequest(BaseSchema):
    name: str = Field(..., examples=["Distribuidora de Tubos Ltda"])
    document_number: Optional[str] = Field(None, examples=["99.888.777/0001-66"])
    email: Optional[str] = Field(None, examples=["financeiro@distribuidora.com.br"])

class CreateScheduleRequest(BaseSchema):
    contact_id: uuid.UUID = Field(..., description="ID do Contato associado a obrigação.", examples=["c95d3e02-4fc8-4228-b223-b1d7d0de04f0"])
    category_id: uuid.UUID = Field(..., description="ID da Categoria (Ex: Materiais, Folha)", examples=["a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6"])
    cost_center_id: uuid.UUID = Field(..., examples=["f1e2d3c4-b5a6-9f8e-7d6c-5b4a3f2e1d0c"])
    description: Optional[str] = Field(None, examples=["Compra de 50 sacos de cimento"])
    value: Decimal = Field(..., gt=0, description="O valor deve ser estritamente positivo", examples=[2500.00])
    issue_date: Optional[date] = Field(None, examples=["2026-04-01"])
    due_date: date = Field(..., description="Data de vencimento do compromisso.", examples=["2026-05-01"])
    
class CreatePaymentRequest(BaseSchema):
    value_paid: Decimal = Field(..., gt=0, description="Amount paid must be strictly positive", examples=[500.00])
    payment_date: date = Field(..., description="Data real do recebimento/pagamento.", examples=["2026-04-02"])
    receipt_document: Optional[str] = Field(None, description="Número de NSU, Boleto ou Cheque.", examples=["NSU-12345"])
