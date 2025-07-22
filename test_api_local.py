#!/usr/bin/env python3
"""
Local API Test Script

This script tests the LinkedIn Job Scraper API locally without Docker.
"""

import os
import sys
import uvicorn
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_import():
    """Test if we can import the API without errors"""
    try:
        from app import app
        print("✅ API module imported successfully")
        return app
    except ImportError as e:
        print(f"❌ Failed to import API: {e}")
        return None

def test_basic_endpoints():
    """Test basic API endpoints"""
    try:
        from app import app
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test health endpoint (without LinkedIn auth)
        response = client.get("/health")
        print(f"📊 Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        
        return True
    except Exception as e:
        print(f"❌ Endpoint testing failed: {e}")
        return False

def run_local_server():
    """Run the API server locally"""
    try:
        from app import app
        print("🚀 Starting local API server...")
        print("📡 Server will be available at: http://localhost:8000")
        print("📖 API docs available at: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    print("🧪 LinkedIn Job Scraper API - Local Test")
    print("=" * 50)
    
    # Test imports
    app = test_api_import()
    if not app:
        sys.exit(1)
    
    # Test basic endpoints
    if test_basic_endpoints():
        print("\n✅ Basic API tests passed!")
    else:
        print("\n❌ Basic API tests failed!")
    
    # Ask user if they want to run the server
    print("\n" + "=" * 50)
    choice = input("Do you want to start the local server? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes']:
        run_local_server()
    else:
        print("👋 Test completed. Use 'python test_api_local.py' to run again.") 