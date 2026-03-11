#!/usr/bin/env python3
"""
Test script to verify backend setup
"""

import sys
import os

def check_imports():
    """Check if all required imports work"""
    print("Checking imports...")
    
    try:
        import fastapi
        print("✓ fastapi")
    except ImportError:
        print("✗ fastapi - run: pip install fastapi")
        return False
    
    try:
        import sqlalchemy
        print("✓ sqlalchemy")
    except ImportError:
        print("✗ sqlalchemy - run: pip install sqlalchemy")
        return False
    
    try:
        import pydantic
        print("✓ pydantic")
    except ImportError:
        print("✗ pydantic - run: pip install pydantic")
        return False
    
    try:
        import jose
        print("✓ python-jose")
    except ImportError:
        print("✗ python-jose - run: pip install python-jose[cryptography]")
        return False
    
    try:
        import passlib
        print("✓ passlib")
    except ImportError:
        print("✗ passlib - run: pip install passlib[bcrypt]")
        return False
    
    return True

def check_structure():
    """Check if project structure is correct"""
    print("\nChecking project structure...")
    
    required_dirs = [
        "core",
        "models", 
        "schemas",
        "auth",
        "routes",
        "services",
        "scripts"
    ]
    
    required_files = [
        "main.py",
        "database.py",
        "run.py",
        "requirements.txt",
        ".env.example"
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ - directory missing")
            all_good = False
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✓ {file_name}")
        else:
            print(f"✗ {file_name} - file missing")
            all_good = False
    
    return all_good

def check_init_files():
    """Check for __init__.py files"""
    print("\nChecking __init__.py files...")
    
    dirs_needing_init = [
        "core",
        "models",
        "schemas",
        "auth",
        "routes",
        "services"
    ]
    
    all_good = True
    
    for dir_name in dirs_needing_init:
        init_file = os.path.join(dir_name, "__init__.py")
        if os.path.exists(init_file):
            print(f"✓ {init_file}")
        else:
            print(f"✗ {init_file} - missing")
            all_good = False
    
    return all_good

def main():
    print("=" * 50)
    print("Audit Analytics Platform - Setup Test")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run checks
    imports_ok = check_imports()
    structure_ok = check_structure()
    init_ok = check_init_files()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    
    if imports_ok and structure_ok and init_ok:
        print("✅ All checks passed!")
        print("\nNext steps:")
        print("1. Configure .env file: cp .env.example .env")
        print("2. Initialize database: python scripts/init_database.py")
        print("3. Run backend: python run.py")
        print("4. Access API docs: http://localhost:8000/docs")
        return 0
    else:
        print("❌ Some checks failed")
        print("\nFix the issues above and run this test again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())