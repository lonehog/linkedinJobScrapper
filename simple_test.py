#!/usr/bin/env python3
"""
Simple API Import Test

This script tests if the API can be imported and basic structure is correct.
"""

import os
import sys

def test_imports():
    """Test if we can import required modules"""
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
        
        import uvicorn
        print("✅ Uvicorn imported successfully")
        
        import pydantic
        print("✅ Pydantic imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import dependencies: {e}")
        return False

def test_scraper_imports():
    """Test if we can import the scraper components"""
    try:
        from scraper_final import linkedin_auth, Config, load_config_from_json
        print("✅ Scraper components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import scraper: {e}")
        return False

def test_api_creation():
    """Test if we can create the FastAPI app"""
    try:
        from app import app
        print("✅ FastAPI app created successfully")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        
        # List all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{list(route.methods)[0]} {route.path}")
        
        print(f"   Available routes: {len(routes)}")
        for route in routes:
            print(f"     - {route}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create API app: {e}")
        return False

if __name__ == "__main__":
    print("🧪 LinkedIn Job Scraper API - Simple Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test basic imports
    print("\n1. Testing basic imports...")
    if not test_imports():
        all_passed = False
    
    # Test scraper imports
    print("\n2. Testing scraper imports...")
    if not test_scraper_imports():
        all_passed = False
    
    # Test API creation
    print("\n3. Testing API creation...")
    if not test_api_creation():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! The API is ready to run.")
        print("💡 To start the server: venv/bin/python app.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("=" * 60) 