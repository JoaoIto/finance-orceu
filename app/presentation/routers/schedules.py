import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.presentation.dependencies import get_organization_id, get_session
from app.application.schemas import (
    ScheduleResponse, CreateScheduleRequest, CreatePaymentRequest, PaymentResponse
)
from app.application.commands import CommandHandler
from app.application.queries import QueryHandler
from app.domain.entities import ScheduleType

# Infrastructure mapping
from app.infrastructure.repositories import (
    SQLScheduleRepository, SQLPaymentRepository
)

router = APIRouter(prefix="/schedules", tags=["Schedules"])

def get_command_handler(db: Session = Depends(get_session)) -> CommandHandler:
    return CommandHandler(
        schedule_repo=SQLScheduleRepository(db),
        payment_repo=SQLPaymentRepository(db)
    )

def get_query_handler(db: Session = Depends(get_session)) -> QueryHandler:
    return QueryHandler(
        schedule_repo=SQLScheduleRepository(db)
    )

@router.post(
    "/debit", 
    response_model=ScheduleResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Criar Agendamento de Débito (A Pagar)",
    responses={400: {"description": "Business Logic Violation"}}
)
def create_debit_schedule(
    dto: CreateScheduleRequest,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: CommandHandler = Depends(get_command_handler)
):
    """
    Cria uma nova obrigação financeira a pagar.
    """
    return handler.create_schedule(org_id, ScheduleType.DEBIT, dto)

@router.post(
    "/credit", 
    response_model=ScheduleResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Criar Agendamento de Crédito (A Receber)",
    responses={400: {"description": "Business Logic Violation"}}
)
def create_credit_schedule(
    dto: CreateScheduleRequest,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: CommandHandler = Depends(get_command_handler)
):
    """
    Cria um novo recebível projetado.
    """
    return handler.create_schedule(org_id, ScheduleType.CREDIT, dto)

@router.get("", response_model=List[ScheduleResponse])
def get_schedules(
    status: Optional[str] = None,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: QueryHandler = Depends(get_query_handler)
):
    return handler.get_schedules(org_id, status)

@router.delete(
    "/{schedule_id}/cancel", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar Agendamento",
    responses={400: {"description": "Business Logic Violation"}}
)
def cancel_schedule(
    schedule_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: CommandHandler = Depends(get_command_handler)
):
    """
    Cancela o agendamento caso ainda não tenha sido pago.
    """
    handler.cancel_schedule(org_id, schedule_id)

@router.post(
    "/{schedule_id}/payments", 
    response_model=PaymentResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar Pagamento ao Agendamento",
    responses={400: {"description": "Estouro Transacional ou Status Inválido"}}
)
def add_payment(
    schedule_id: uuid.UUID,
    dto: CreatePaymentRequest,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: CommandHandler = Depends(get_command_handler)
):
    """
    Adiciona um pagamento a este agendamento e executa as regras 
    de validação contra valor acima do teto.
    """
    return handler.add_payment(org_id, schedule_id, dto)
