import pytest
import uuid
from decimal import Decimal
from datetime import date

from app.domain.entities import Schedule, Payment, ScheduleType, ScheduleStatus

def test_schedule_can_receive_valid_payment():
    # Arrange
    schedule = Schedule(
        organization_id=uuid.uuid4(),
        contact_id=uuid.uuid4(),
        category_id=uuid.uuid4(),
        cost_center_id=uuid.uuid4(),
        type=ScheduleType.DEBIT,
        value=Decimal("1500.00"),
        due_date=date(2026, 5, 1)
    )
    
    # Act & Assert
    assert schedule.can_receive_payment(Decimal("500.00")) == True

def test_schedule_blocks_extravagant_payment():
    schedule = Schedule(
        organization_id=uuid.uuid4(),
        contact_id=uuid.uuid4(),
        category_id=uuid.uuid4(),
        cost_center_id=uuid.uuid4(),
        type=ScheduleType.DEBIT,
        value=Decimal("500.00"),
        due_date=date(2026, 5, 1)
    )
    
    # Should not allow 600
    assert schedule.can_receive_payment(Decimal("600.00")) == False

def test_schedule_status_changes_dynamically_when_paid():
    schedule = Schedule(
        organization_id=uuid.uuid4(),
        contact_id=uuid.uuid4(),
        category_id=uuid.uuid4(),
        cost_center_id=uuid.uuid4(),
        type=ScheduleType.DEBIT,
        value=Decimal("100.00"),
        due_date=date(2026, 5, 1)
    )
    
    assert schedule.status == ScheduleStatus.OPEN
    
    # Add fake payment directly to the list to simulate Repository loading
    payment = Payment(
        organization_id=schedule.organization_id,
        schedule_id=schedule.id,
        value_paid=Decimal("100.00"),
        payment_date=date.today()
    )
    schedule.payments.append(payment)
    
    assert schedule.status == ScheduleStatus.PAID
