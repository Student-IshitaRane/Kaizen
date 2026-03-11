#!/usr/bin/env python3
"""
Quick test to verify the backend can start
"""

import sys
import os

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    
    try:
        from main import app
        print("✓ Main application imports")
    except Exception as e:
        print(f"✗ Main import failed: {e}")
        return False
    
    try:
        from database import engine, Base, get_db
        print("✓ Database imports")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        return False
    
    try:
        from core.config import settings
        print(f"✓ Config loaded: ENVIRONMENT={settings.ENVIRONMENT}")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database connection"""
    print("\nTesting database...")
    
    try:
        from database import engine, Base
        from models import User, Vendor
        
        # Try to create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables can be created")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_routes():
    """Test that routes are registered"""
    print("\nTesting routes...")
    
    try:
        from main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        expected_routes = ['/', '/health', '/system-info', '/auth', '/upload', '/transactions', '/cases', '/reviews']
        
        print(f"Found {len(routes)} routes")
        print("Sample routes:")
        for i, route in enumerate(routes[:10]):
            print(f"  {route}")
        
        return True
    except Exception as e:
        print(f"✗ Routes test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Quick Test for Audit Analytics Platform")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run tests
    imports_ok = test_imports()
    database_ok = test_database()
    routes_ok = test_routes()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    if imports_ok and database_ok and routes_ok:
        print("✅ All tests passed!")
        print("\nYou can now run the backend with:")
        print("  python run.py")
        print("\nAccess the API at:")
        print("  http://localhost:8000/docs")
        return 0
    else:
        print("❌ Some tests failed")
        print("\nCommon issues:")
        print("1. Dependencies not installed: pip install -r minimal_requirements.txt")
        print("2. Missing __init__.py files in directories")
        print("3. Database connection issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())