import uuid
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session

from app.presentation.dependencies import get_organization_id, get_session
from app.application.schemas import (
    ScheduleResponse, CreateScheduleRequest, CreatePaymentRequest, PaymentResponse,
    SchedulePaginatedResponse, SummaryResponse
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
    responses={400: {"description": "Business Logic Violation"}},
    tags=["Schedules"]
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
    responses={400: {"description": "Business Logic Violation"}},
    tags=["Schedules"]
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

@router.get("", response_model=SchedulePaginatedResponse, summary="Listar e Filtrar Agendamentos (OData Nibo Pattern)", tags=["Schedules"])
def get_schedules(
    type: Optional[str] = Query(None, description="Tipo: DEBIT ou CREDIT"),
    status: Optional[str] = Query(None, description="Status: OPEN, PAID ou OVERDUE"),
    due_date_from: Optional[date] = Query(None, description="Data de vencimento inicial"),
    due_date_to: Optional[date] = Query(None, description="Data de vencimento final"),
    category_id: Optional[uuid.UUID] = Query(None, description="ID da Categoria"),
    cost_center_id: Optional[uuid.UUID] = Query(None, description="ID do Centro de Custo"),
    contact_id: Optional[uuid.UUID] = Query(None, description="ID do Contato"),
    skip: int = Query(0, ge=0, description="Registros a pular (OData $skip)"),
    top: int = Query(50, ge=1, le=500, description="Tamanho da página (OData $top)"),
    order_by: str = Query("dueDate", description="Ordenação (ex: dueDate, -dueDate) (OData $orderBy)"),
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: QueryHandler = Depends(get_query_handler)
):
    """
    Retorna uma lista paginada de todos os agendamentos financeiros. 
    O status é calculado em tempo real com base nos pagamentos recebidos.
    """
    total, items = handler.get_schedules(
        org_id, type, status, due_date_from, due_date_to,
        category_id, cost_center_id, contact_id, skip, top, order_by
    )
    return SchedulePaginatedResponse(total=total, skip=skip, top=top, items=items)

@router.get("/summary", response_model=SummaryResponse, summary="Resumo/Fluxo de Caixa Periódico", tags=["Schedules"])
def get_summary(
    due_date_from: Optional[date] = Query(None, description="Data de vencimento inicial"),
    due_date_to: Optional[date] = Query(None, description="Data de vencimento final"),
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: QueryHandler = Depends(get_query_handler)
):
    data = handler.get_schedule_summary(org_id, due_date_from, due_date_to)
    
    return SummaryResponse(
        items=[data] if due_date_from or due_date_to else [],
        grand_total_debit=data["total_debit"],
        grand_total_credit=data["total_credit"],
        grand_balance=data["balance"]
    )

@router.get("/{schedule_id}", response_model=ScheduleResponse, summary="Detalhar Agendamento", tags=["Schedules"])
def get_schedule(
    schedule_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: QueryHandler = Depends(get_query_handler)
):
    schedule = handler.get_schedule(org_id, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Agenda não encontrada")
    return schedule

@router.delete(
    "/{schedule_id}/cancel", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar Agendamento",
    responses={400: {"description": "Business Logic Violation"}},
    tags=["Schedules"]
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
    responses={400: {"description": "Estouro Transacional ou Status Inválido"}},
    tags=["Schedules"]
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
