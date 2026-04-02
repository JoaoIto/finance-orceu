import uuid
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db

async def get_organization_id(x_organization_id: str = Header(..., description="UUID of the Organization Tenant")) -> uuid.UUID:
    """
    Middleware/Dependency SIMULATING an Authentication Header.
    In real life this would be extracted from a JWT token.
    """
    try:
        return uuid.UUID(x_organization_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Organization ID. Must be a UUID.")

def get_session(db: Session = Depends(get_db)) -> Session:
    return db
