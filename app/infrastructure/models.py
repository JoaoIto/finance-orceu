import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database import Base

class ScheduleType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    tax_id = Column(String(20), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    contacts = relationship("Contact", back_populates="organization", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="organization", cascade="all, delete-orphan")
    cost_centers = relationship("CostCenter", back_populates="organization", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="organization", cascade="all, delete-orphan")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    document_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    organization = relationship("Organization", back_populates="contacts")
    schedules = relationship("Schedule", back_populates="contact")

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)

    organization = relationship("Organization", back_populates="categories")
    schedules = relationship("Schedule", back_populates="category")

class CostCenter(Base):
    __tablename__ = "cost_centers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)

    organization = relationship("Organization", back_populates="cost_centers")
    schedules = relationship("Schedule", back_populates="cost_center")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    # RESTRICT constraint on deletion for safety as mentioned in Deep Dive
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="RESTRICT"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id", ondelete="RESTRICT"), nullable=False)
    
    type = Column(Enum(ScheduleType), nullable=False)
    description = Column(String(255), nullable=True)
    value = Column(Numeric(15, 2), nullable=False)
    issue_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="schedules")
    contact = relationship("Contact", back_populates="schedules")
    category = relationship("Category", back_populates="schedules")
    cost_center = relationship("CostCenter", back_populates="schedules")
    payments = relationship("Payment", back_populates="schedule", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("schedules.id", ondelete="RESTRICT"), nullable=False)
    
    value_paid = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    receipt_document = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    schedule = relationship("Schedule", back_populates="payments")
