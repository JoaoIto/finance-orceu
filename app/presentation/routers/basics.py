import uuid
from fastapi import APIRouter, Depends, status
from typing import List

from app.presentation.dependencies import get_organization_id, get_session
from app.application.schemas import (
    ContactResponse, CategoryResponse, CostCenterResponse,
    CreateContactRequest, CreateCategoryRequest, CreateCostCenterRequest
)
from app.application.commands import CommandHandler
from app.application.queries import QueryHandler
from app.infrastructure.repositories import (
    SQLContactRepository, SQLCategoryRepository, SQLCostCenterRepository, 
    SQLScheduleRepository
)
from sqlalchemy.orm import Session

router = APIRouter()

def get_command_handler(db: Session = Depends(get_session)) -> CommandHandler:
    return CommandHandler(
        schedule_repo=SQLScheduleRepository(db),
        contact_repo=SQLContactRepository(db),
        category_repo=SQLCategoryRepository(db),
        cost_center_repo=SQLCostCenterRepository(db)
    )

def get_query_handler(db: Session = Depends(get_session)) -> QueryHandler:
    return QueryHandler(
        schedule_repo=SQLScheduleRepository(db),
        contact_repo=SQLContactRepository(db),
        category_repo=SQLCategoryRepository(db),
        cost_center_repo=SQLCostCenterRepository(db)
    )

@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    dto: CreateContactRequest,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: CommandHandler = Depends(get_command_handler)
):
    return handler.create_contact(org_id, dto)

@router.get("/contacts", response_model=List[ContactResponse])
def get_contacts(
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: QueryHandler = Depends(get_query_handler)
):
    return handler.get_contacts(org_id)

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    dto: CreateCategoryRequest,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: CommandHandler = Depends(get_command_handler)
):
    return handler.create_category(org_id, dto)

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: QueryHandler = Depends(get_query_handler)
):
    return handler.get_categories(org_id)

@router.post("/cost_centers", response_model=CostCenterResponse, status_code=status.HTTP_201_CREATED)
def create_cost_center(
    dto: CreateCostCenterRequest,
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: CommandHandler = Depends(get_command_handler)
):
    return handler.create_cost_center(org_id, dto)

@router.get("/cost_centers", response_model=List[CostCenterResponse])
def get_cost_centers(
    org_id: uuid.UUID = Depends(get_organization_id),
    handler: QueryHandler = Depends(get_query_handler)
):
    return handler.get_cost_centers(org_id)
