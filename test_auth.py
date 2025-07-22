#!/usr/bin/env python3
"""
LinkedIn Authentication Test Script

This script tests the LinkedIn authentication functionality without running the full scraper.
Use this to verify your credentials and authentication setup before running the main scraper.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_setup():
    """Test if environment variables are properly set."""
    print("🔍 Testing Environment Setup...")
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    debug = os.getenv('DEBUG_MODE', 'false')
    
    if not email:
        print("❌ LINKEDIN_EMAIL not found in environment variables")
        return False
    
    if not password:
        print("❌ LINKEDIN_PASSWORD not found in environment variables")
        return False
    
    print(f"✅ Email: {email[:3]}***@{email.split('@')[1] if '@' in email else 'unknown'}")
    print(f"✅ Password: {'*' * len(password)} (length: {len(password)})")
    print(f"✅ Debug Mode: {debug}")
    
    return True

def test_dependencies():
    """Test if required dependencies are installed."""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        'requests',
        'beautifulsoup4', 
        'pandas',
        'python-dotenv',
        'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                import bs4
                print(f"✅ BeautifulSoup4: {bs4.__version__}")
            elif package == 'python-dotenv':
                import dotenv
                print(f"✅ python-dotenv: installed")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {package}: {version}")
        except ImportError:
            print(f"❌ {package}: Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🚨 Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True

def test_linkedin_connection():
    """Test basic connectivity to LinkedIn."""
    print("\n🌐 Testing LinkedIn Connectivity...")
    
    try:
        import requests
        
        # Test basic connectivity
        response = requests.get('https://www.linkedin.com', timeout=10)
        if response.status_code == 200:
            print("✅ LinkedIn is accessible")
            return True
        else:
            print(f"❌ LinkedIn returned status code: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Failed to connect to LinkedIn: {e}")
        return False

def test_authentication():
    """Test LinkedIn authentication with provided credentials."""
    print("\n🔐 Testing LinkedIn Authentication...")
    
    try:
        # Import the authentication class from the main scraper
        from scraper_final import LinkedInAuth
        
        # Create auth instance and attempt login
        auth = LinkedInAuth()
        
        print("Attempting to authenticate with LinkedIn...")
        success = auth.login()
        
        if success:
            print("✅ LinkedIn authentication successful!")
            return True
        else:
            print("❌ LinkedIn authentication failed")
            print("Check your credentials and account status")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import authentication module: {e}")
        return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def main():
    """Run all authentication tests."""
    print("🚀 LinkedIn Scraper Authentication Test")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Dependencies", test_dependencies), 
        ("LinkedIn Connectivity", test_linkedin_connection),
        ("LinkedIn Authentication", test_authentication)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your scraper is ready to run.")
        print("\nNext steps:")
        print("1. Run: python scraper_final.py")
        print("2. Or use Docker: docker-compose up --build")
        return True
    else:
        print("🚨 Some tests failed. Please address the issues above.")
        print("\nCommon solutions:")
        print("1. Check your .env file has correct credentials")
        print("2. Install missing dependencies: pip install -r requirements.txt")
        print("3. Verify your LinkedIn account is accessible")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 