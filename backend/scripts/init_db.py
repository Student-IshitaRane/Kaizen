import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.session import engine, Base
from app.database.models import *

def init_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()