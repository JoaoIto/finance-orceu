import pytest
import uuid
from decimal import Decimal
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.infrastructure.database import Base, get_db
from app.infrastructure import models

# Setup In-Memory Database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
ORG_ID = str(uuid.uuid4())
HEADERS = {"x-organization-id": ORG_ID}

@pytest.fixture(scope="module", autouse=True)
def setup_basics():
    # Setup standard required items
    contact = client.post("/api/v1/contacts", json={"name": "Test Contact"}, headers=HEADERS).json()
    category = client.post("/api/v1/categories", json={"name": "Test Cat"}, headers=HEADERS).json()
    cc = client.post("/api/v1/cost_centers", json={"name": "Test CC"}, headers=HEADERS).json()
    
    return {
        "contact_id": contact["id"],
        "category_id": category["id"],
        "cost_center_id": cc["id"]
    }

def test_missing_auth_header():
    response = client.get("/api/v1/contacts")
    assert response.status_code == 422 # missing dependency

def test_create_schedule_and_prevent_overpayment(setup_basics):
    # 1. Create a Schedule of 100.00
    sched_payload = {
        "contact_id": setup_basics["contact_id"],
        "category_id": setup_basics["category_id"],
        "cost_center_id": setup_basics["cost_center_id"],
        "value": "100.00",
        "due_date": "2026-05-01"
    }
    resp = client.post("/api/v1/schedules/debit", json=sched_payload, headers=HEADERS)
    assert resp.status_code == 201
    schedule_id = resp.json()["id"]
    
    # 2. Try to pay 150.00 (which is an overflow)
    pay_payload = {
        "value_paid": "150.00",
        "payment_date": "2026-04-02"
    }
    pay_resp = client.post(f"/api/v1/schedules/{schedule_id}/payments", json=pay_payload, headers=HEADERS)
    
    # 3. Assert global domain exception handler catches it with HTTP 400
    assert pay_resp.status_code == 400
    assert "Business Logic Violation" in pay_resp.json()["error"]
    assert "limite" in pay_resp.json()["message"]
