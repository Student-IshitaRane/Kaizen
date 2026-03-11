import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database import engine, Base
from models import user, vendor, purchase_ledger, sales_ledger, general_ledger, bank_transaction, flagged_case, review_action

def init_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    print("\nTables created:")
    print("- users")
    print("- vendors")
    print("- purchase_ledger")
    print("- sales_ledger")
    print("- general_ledger")
    print("- bank_transactions")
    print("- flagged_cases")
    print("- review_actions")

if __name__ == "__main__":
    init_database()