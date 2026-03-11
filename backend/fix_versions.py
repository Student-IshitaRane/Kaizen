#!/usr/bin/env python3
"""
Try to fix version compatibility issues
"""

import subprocess
import sys

def install_packages():
    """Install compatible versions"""
    print("Installing compatible versions...")
    
    # Uninstall problematic packages first
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pydantic-settings"], 
                   capture_output=True)
    
    # Install compatible versions
    packages = [
        "fastapi==0.103.0",
        "uvicorn[standard]==0.23.2", 
        "sqlalchemy==2.0.20",
        "pydantic==1.10.11",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "aiofiles==23.2.1"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to install {package}: {result.stderr}")
    
    print("\nInstallation complete!")

def test_import():
    """Test if imports work"""
    print("\nTesting imports...")
    
    try:
        import fastapi
        print(f"✓ fastapi {fastapi.__version__}")
    except Exception as e:
        print(f"✗ fastapi: {e}")
        return False
    
    try:
        import pydantic
        print(f"✓ pydantic {pydantic.__version__}")
    except Exception as e:
        print(f"✗ pydantic: {e}")
        return False
    
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Test", version="1.0.0")
        print("✓ FastAPI app creation")
        return True
    except Exception as e:
        print(f"✗ FastAPI app creation: {e}")
        return False

def main():
    print("=" * 50)
    print("Fixing version compatibility")
    print("=" * 50)
    
    install_packages()
    
    if test_import():
        print("\n✅ Success! Versions are compatible.")
        print("\nYou can now run: python run.py")
    else:
        print("\n❌ Still having issues.")
        print("\nTry manually installing:")
        print("pip install fastapi==0.95.0 uvicorn[standard]==0.21.0 sqlalchemy==2.0.0 pydantic==1.10.0")

if __name__ == "__main__":
    main()