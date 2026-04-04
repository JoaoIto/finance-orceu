import uuid
from typing import List, Optional, Tuple
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.domain import entities
from app.domain.repositories import (
    OrganizationRepository, ContactRepository, CategoryRepository,
    CostCenterRepository, ScheduleRepository, PaymentRepository
)
from app.infrastructure import models

class SQLOrganizationRepository(OrganizationRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, org_id: uuid.UUID) -> Optional[entities.Organization]:
        db_org = self.session.query(models.Organization).filter(models.Organization.id == org_id).first()
        if not db_org: return None
        return entities.Organization.model_validate(db_org)

class SQLContactRepository(ContactRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, contact: entities.Contact) -> entities.Contact:
        db_contact = models.Contact(**contact.model_dump(exclude={'created_at'}))
        self.session.add(db_contact)
        self.session.commit()
        self.session.refresh(db_contact)
        return entities.Contact.model_validate(db_contact)

    def get_all(self, org_id: uuid.UUID) -> List[entities.Contact]:
        db_items = self.session.query(models.Contact).filter(models.Contact.organization_id == org_id).all()
        return [entities.Contact.model_validate(i) for i in db_items]

class SQLCategoryRepository(CategoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, category: entities.Category) -> entities.Category:
        db_cat = models.Category(**category.model_dump(exclude={'created_at'}))
        self.session.add(db_cat)
        self.session.commit()
        self.session.refresh(db_cat)
        return entities.Category.model_validate(db_cat)

    def get_all(self, org_id: uuid.UUID) -> List[entities.Category]:
        db_items = self.session.query(models.Category).filter(models.Category.organization_id == org_id).all()
        return [entities.Category.model_validate(i) for i in db_items]


class SQLCostCenterRepository(CostCenterRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, cost_center: entities.CostCenter) -> entities.CostCenter:
        db_cc = models.CostCenter(**cost_center.model_dump(exclude={'created_at'}))
        self.session.add(db_cc)
        self.session.commit()
        self.session.refresh(db_cc)
        return entities.CostCenter.model_validate(db_cc)

    def get_all(self, org_id: uuid.UUID) -> List[entities.CostCenter]:
        db_items = self.session.query(models.CostCenter).filter(models.CostCenter.organization_id == org_id).all()
        return [entities.CostCenter.model_validate(i) for i in db_items]


class SQLScheduleRepository(ScheduleRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, db_schedule: models.Schedule) -> entities.Schedule:
        # Load payments implicitly when converting to model
        domain_payments = [entities.Payment.model_validate(p) for p in db_schedule.payments]
        domain_sched = entities.Schedule.model_validate(db_schedule)
        domain_sched.payments = domain_payments
        return domain_sched

    def create(self, schedule: entities.Schedule) -> entities.Schedule:
        db_sched = models.Schedule(
            id=schedule.id,
            organization_id=schedule.organization_id,
            contact_id=schedule.contact_id,
            category_id=schedule.category_id,
            cost_center_id=schedule.cost_center_id,
            type=schedule.type,
            description=schedule.description,
            value=schedule.value,
            issue_date=schedule.issue_date,
            due_date=schedule.due_date,
            created_at=schedule.created_at
        )
        self.session.add(db_sched)
        try:
            self.session.commit()
            self.session.refresh(db_sched)
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Foreign key constraint failed. Check if contact, category or cost_center exist.")
            
        return self._to_domain(db_sched)

    def get_by_id(self, org_id: uuid.UUID, schedule_id: uuid.UUID) -> Optional[entities.Schedule]:
        db_sched = self.session.query(models.Schedule)\
            .filter(models.Schedule.organization_id == org_id, models.Schedule.id == schedule_id)\
            .first()
        if not db_sched: return None
        return self._to_domain(db_sched)

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
    ) -> Tuple[int, List[entities.Schedule]]:
        
        query = self.session.query(models.Schedule).filter(models.Schedule.organization_id == org_id)

        if type: query = query.filter(models.Schedule.type == type)
        if due_date_from: query = query.filter(models.Schedule.due_date >= due_date_from)
        if due_date_to: query = query.filter(models.Schedule.due_date <= due_date_to)
        if category_id: query = query.filter(models.Schedule.category_id == category_id)
        if cost_center_id: query = query.filter(models.Schedule.cost_center_id == cost_center_id)
        if contact_id: query = query.filter(models.Schedule.contact_id == contact_id)

        # Ordering (OData Pattern)
        if order_by == "dueDate":
            query = query.order_by(models.Schedule.due_date.asc())
        elif order_by == "-dueDate":
            query = query.order_by(models.Schedule.due_date.desc())
        elif order_by == "value":
            query = query.order_by(models.Schedule.value.asc())
        elif order_by == "-value":
            query = query.order_by(models.Schedule.value.desc())
        else:
            query = query.order_by(models.Schedule.due_date.asc())

        db_items = query.all()
        # Mapeamento e list comprehension de status virtual
        domain_items = [self._to_domain(i) for i in db_items]
        
        if status:
            domain_items = [i for i in domain_items if i.status == status]
            
        # Paginação OData In-Memory (Top e Skip)
        total_items = len(domain_items)
        end_idx = skip + top
        
        paginated_items = domain_items[skip:end_idx]
            
        return total_items, paginated_items
        
    def get_summary(
        self, 
        org_id: uuid.UUID,
        due_date_from: Optional[date] = None,
        due_date_to: Optional[date] = None
    ) -> dict:
        query = self.session.query(models.Schedule).filter(models.Schedule.organization_id == org_id)
        
        if due_date_from: query = query.filter(models.Schedule.due_date >= due_date_from)
        if due_date_to: query = query.filter(models.Schedule.due_date <= due_date_to)
        
        db_items = query.all()
        domain_items = [self._to_domain(i) for i in db_items]
        
        # Agrupamento (simplificado para uma única métrica do periodo requested)
        total_debit = Decimal(0)
        total_credit = Decimal(0)
        
        for item in domain_items:
            # Em relatório financeiro, geralmente usa-se o status, mas assumiremos tudo que tem dueDate
            if item.type == entities.ScheduleType.DEBIT:
                total_debit += min(item.value, item.total_paid) if item.status == 'PAID' else item.value
            if item.type == entities.ScheduleType.CREDIT:
                total_credit += min(item.value, item.total_paid) if item.status == 'PAID' else item.value
                
        return {
            "period": f"{due_date_from} to {due_date_to}",
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance": total_credit - total_debit
        }

    def cancel(self, org_id: uuid.UUID, schedule_id: uuid.UUID) -> bool:
        db_sched = self.session.query(models.Schedule).filter(
            models.Schedule.organization_id == org_id, 
            models.Schedule.id == schedule_id
        ).first()
        if not db_sched:
            return False
        self.session.delete(db_sched)
        self.session.commit()
        return True


class SQLPaymentRepository(PaymentRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, payment: entities.Payment) -> entities.Payment:
        db_pay = models.Payment(**payment.model_dump())
        self.session.add(db_pay)
        self.session.commit()
        self.session.refresh(db_pay)
        return entities.Payment.model_validate(db_pay)

    def get_by_schedule_id(self, org_id: uuid.UUID, schedule_id: uuid.UUID) -> List[entities.Payment]:
        db_items = self.session.query(models.Payment).filter(
            models.Payment.organization_id == org_id,
            models.Payment.schedule_id == schedule_id
        ).all()
        return [entities.Payment.model_validate(i) for i in db_items]
