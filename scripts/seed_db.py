import sys
import os
import uuid

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.database import SessionLocal, Base, engine
from app.infrastructure.models import Organization, Contact, Category, CostCenter

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    org_id = uuid.UUID("99999999-9999-4999-9999-999999999999")
    
    if db.query(Organization).filter(Organization.id == org_id).first():
        print("Seed already executed.")
        db.close()
        return

    print("Executing Seed...")
    org = Organization(id=org_id, name="Orceu Construtora Matriz", tax_id="000.000.000/0001-00")
    db.add(org)
    
    # Defaults
    contact = Contact(organization_id=org_id, name="Fornecedor Padrão LTDA", document_number="12.345.678/0001-99")
    cat_debit = Category(organization_id=org_id, name="Material de Construção")
    cat_credit = Category(organization_id=org_id, name="Recebimento de Cliente")
    cc = CostCenter(organization_id=org_id, name="Obra Edifício Alpha")
    
    db.add(contact)
    db.add(cat_debit)
    db.add(cat_credit)
    db.add(cc)
    
    db.commit()
    print(f"Seed success! \n--> ORGANIZATION_ID tenant = {org_id}")
    db.close()

if __name__ == "__main__":
    seed()
