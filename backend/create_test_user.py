from database import SessionLocal
from models.user import User

db = SessionLocal()

# Check if user exists
existing = db.query(User).filter(User.email == "test@example.com").first()
if existing:
    print("User already exists")
else:
    # Create test user with plain password for testing
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash="password123",  # Plain text for testing
        role="auditor",
        is_active=True
    )
    db.add(user)
    db.commit()
    print("Test user created: test@example.com / password123")

db.close()
