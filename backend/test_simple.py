#!/usr/bin/env python3
"""
Simple test to check if basic imports work
"""

import sys
import os

def test_imports():
    """Test if we can import the main modules"""
    print("Testing imports...")
    
    try:
        from database import engine, Base, get_db
        print("✓ Database imports OK")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        return False
    
    try:
        from core.config import settings
        print("✓ Config import OK")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from models.user import User
        from models.vendor import Vendor
        print("✓ Model imports OK")
    except Exception as e:
        print(f"✗ Model import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database connection"""
    print("\nTesting database...")
    try:
        from database import engine, Base
        from models.user import User
        from models.vendor import Vendor
        
        # Try to create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables can be created")
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from core.config import settings
        print(f"  Environment: {settings.ENVIRONMENT}")
        print(f"  Database URL: {settings.DATABASE_URL[:30]}...")
        print(f"  Upload dir: {settings.UPLOAD_DIR}")
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Audit Analytics Platform - Quick Test")
    print("=" * 50)
    
    # Add current directory to path
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Test imports
    if not test_imports():
        return 1
    
    # Test config
    if not test_config():
        return 1
    
    # Test database
    if not test_database():
        return 1
    
    print("\n" + "=" * 50)
    print("✅ All basic tests passed!")
    print("\nYou can now run the server with:")
    print("  python run.py")
    print("\nOr test the API with:")
    print("  python quick_test.py")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())