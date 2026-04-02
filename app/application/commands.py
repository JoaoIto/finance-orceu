import uuid
from typing import Dict, Any

from app.domain.entities import (
    Schedule, Payment, ScheduleType, ScheduleStatus,
    Category, CostCenter, Contact
)
from app.domain.repositories import (
    ScheduleRepository, PaymentRepository, CategoryRepository,
    CostCenterRepository, ContactRepository
)
from app.application.schemas import (
    CreateScheduleRequest, CreatePaymentRequest,
    CreateCategoryRequest, CreateCostCenterRequest, CreateContactRequest
)

class CommandHandler:
    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        payment_repo: PaymentRepository = None,
        category_repo: CategoryRepository = None,
        cost_center_repo: CostCenterRepository = None,
        contact_repo: ContactRepository = None
    ):
        self.schedule_repo = schedule_repo
        self.payment_repo = payment_repo
        self.category_repo = category_repo
        self.cost_center_repo = cost_center_repo
        self.contact_repo = contact_repo

    def create_category(self, org_id: uuid.UUID, dto: CreateCategoryRequest) -> Category:
        category = Category(organization_id=org_id, name=dto.name)
        return self.category_repo.create(category)
        
    def create_cost_center(self, org_id: uuid.UUID, dto: CreateCostCenterRequest) -> CostCenter:
        cost_center = CostCenter(organization_id=org_id, name=dto.name)
        return self.cost_center_repo.create(cost_center)
        
    def create_contact(self, org_id: uuid.UUID, dto: CreateContactRequest) -> Contact:
        contact = Contact(
            organization_id=org_id, 
            name=dto.name,
            document_number=dto.document_number,
            email=dto.email
        )
        return self.contact_repo.create(contact)

    def create_schedule(self, org_id: uuid.UUID, type: ScheduleType, dto: CreateScheduleRequest) -> Schedule:
        schedule = Schedule(
            organization_id=org_id,
            contact_id=dto.contact_id,
            category_id=dto.category_id,
            cost_center_id=dto.cost_center_id,
            type=type,
            description=dto.description,
            value=dto.value,
            issue_date=dto.issue_date,
            due_date=dto.due_date
        )
        return self.schedule_repo.create(schedule)

    def cancel_schedule(self, org_id: uuid.UUID, schedule_id: uuid.UUID):
        # Business Rule: Cannot delete a paid schedule
        schedule = self.schedule_repo.get_by_id(org_id, schedule_id)
        if not schedule:
            raise ValueError("Schedule not found")
            
        if schedule.status == ScheduleStatus.PAID:
            raise ValueError("Cannot cancel a schedule that is already fully paid")
            
        success = self.schedule_repo.cancel(org_id, schedule_id)
        if not success:
            raise ValueError("Failed to cancel schedule")
        return True

    def add_payment(self, org_id: uuid.UUID, schedule_id: uuid.UUID, dto: CreatePaymentRequest) -> Payment:
        schedule = self.schedule_repo.get_by_id(org_id, schedule_id)
        if not schedule:
            raise ValueError("Schedule not found")
            
        # Business Rule Verification: Anti-extravagant payment
        if not schedule.can_receive_payment(dto.value_paid):
            raise ValueError(f"Estouro Transacional: Pagamento de {dto.value_paid} excede o limite de {schedule.value - schedule.total_paid} restante.")
            
        payment = Payment(
            organization_id=org_id,
            schedule_id=schedule_id,
            value_paid=dto.value_paid,
            payment_date=dto.payment_date,
            receipt_document=dto.receipt_document
        )
        saved_payment = self.payment_repo.create(payment)
        
        # Adding to the domain object simply to reflect the state after
        schedule.payments.append(saved_payment)
        
        return saved_payment
