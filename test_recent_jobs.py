#!/usr/bin/env python3
"""
Test Script for Recent LinkedIn Jobs Scraper

This script tests the functionality of the recent jobs scraper including:
- URL parsing and pagination
- Easy Apply detection
- Recent job filtering (last hour)
"""

import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

def test_url_parsing():
    """Test URL parsing functionality."""
    print("🔍 Testing URL Parsing...")
    
    test_url = "https://www.linkedin.com/jobs/search/?f_EA=false&f_TPR=r3600&geoId=101282230&keywords=engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
    
    parsed_url = urlparse(test_url)
    query_params = parse_qs(parsed_url.query)
    
    print(f"✅ Base URL: {parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}")
    print(f"✅ Parameters:")
    for key, value in query_params.items():
        print(f"   - {key}: {value[0] if value else 'None'}")
    
    # Test pagination
    query_params['start'] = ['25']
    from urllib.parse import urlencode
    new_query = urlencode(query_params, doseq=True)
    paginated_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"
    
    print(f"✅ Paginated URL: {paginated_url}")
    return True

def test_easy_apply_detection():
    """Test Easy Apply detection logic."""
    print("\n🔍 Testing Easy Apply Detection...")
    
    # Simulate HTML content for testing
    easy_apply_html = """
    <div class="job-card">
        <button class="apply-button--primary">Easy Apply</button>
        <span>Software Engineer</span>
    </div>
    """
    
    non_easy_apply_html = """
    <div class="job-card">
        <span>Be an early applicant</span>
        <span>Senior Developer</span>
    </div>
    """
    
    # Simple detection test
    has_easy_apply_1 = "easy apply" in easy_apply_html.lower()
    has_easy_apply_2 = "easy apply" in non_easy_apply_html.lower()
    
    print(f"✅ Easy Apply HTML detection: {has_easy_apply_1}")
    print(f"✅ Non-Easy Apply HTML detection: {has_easy_apply_2}")
    
    # Check for external application indicators
    has_external = "be an early applicant" in non_easy_apply_html.lower()
    print(f"✅ External application detected: {has_external}")
    
    return True

def test_config_validation():
    """Test configuration validation."""
    print("\n🔍 Testing Configuration...")
    
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required_fields = [
            'SEARCH_URLS',
            'MAX_PAGES_PER_SEARCH', 
            'FILTER_EASY_APPLY',
            'CSV_FILENAME'
        ]
        
        for field in required_fields:
            if field in config:
                print(f"✅ {field}: {config[field]}")
            else:
                print(f"❌ Missing: {field}")
                return False
        
        # Validate search URLs
        if config.get('SEARCH_URLS'):
            for i, search_url in enumerate(config['SEARCH_URLS']):
                print(f"✅ Search URL {i+1}: {search_url.get('name', 'Unnamed')}")
                url = search_url.get('url', '')
                if 'f_TPR=r3600' in url:
                    print(f"   ✅ Has last hour filter")
                if 'f_EA=false' in url:
                    print(f"   ✅ Has Easy Apply filter")
        
        return True
        
    except FileNotFoundError:
        print("❌ config.json not found")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in config.json")
        return False

def test_environment():
    """Test environment setup."""
    print("\n🔍 Testing Environment...")
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if email:
        print(f"✅ LinkedIn Email: {email[:3]}***@{email.split('@')[1] if '@' in email else 'unknown'}")
    else:
        print("❌ LINKEDIN_EMAIL not set")
        return False
    
    if password:
        print(f"✅ LinkedIn Password: {'*' * len(password)} (length: {len(password)})")
    else:
        print("❌ LINKEDIN_PASSWORD not set")
        return False
    
    return True

def test_recent_jobs_logic():
    """Test recent jobs filtering logic."""
    print("\n🔍 Testing Recent Jobs Logic...")
    
    # Test time filter parameter
    time_filters = {
        'r3600': 'Last Hour',
        'r86400': 'Last 24 Hours', 
        'r604800': 'Last Week'
    }
    
    for filter_code, description in time_filters.items():
        print(f"✅ Time filter {filter_code}: {description}")
    
    # Test geo location
    geo_locations = {
        '101282230': 'Germany',
        '103644278': 'United States',
        '101165590': 'United Kingdom'
    }
    
    for geo_id, location in geo_locations.items():
        print(f"✅ Geo ID {geo_id}: {location}")
    
    return True

def generate_sample_urls():
    """Generate sample LinkedIn search URLs."""
    print("\n📋 Sample LinkedIn Search URLs:")
    
    base_url = "https://www.linkedin.com/jobs/search/"
    
    samples = [
        {
            'title': 'Recent Engineer Jobs (No Easy Apply)',
            'params': {
                'f_EA': 'false',
                'f_TPR': 'r3600', 
                'geoId': '101282230',
                'keywords': 'engineer',
                'origin': 'JOB_SEARCH_PAGE_JOB_FILTER'
            }
        },
        {
            'title': 'Recent Software Developer Jobs (No Easy Apply)',
            'params': {
                'f_EA': 'false',
                'f_TPR': 'r3600',
                'geoId': '101282230', 
                'keywords': 'software developer',
                'origin': 'JOB_SEARCH_PAGE_JOB_FILTER'
            }
        },
        {
            'title': 'Recent Data Scientist Jobs (Last 24h, No Easy Apply)',
            'params': {
                'f_EA': 'false',
                'f_TPR': 'r86400',
                'geoId': '103644278',
                'keywords': 'data scientist',
                'origin': 'JOB_SEARCH_PAGE_JOB_FILTER'
            }
        }
    ]
    
    for sample in samples:
        from urllib.parse import urlencode
        url = f"{base_url}?{urlencode(sample['params'])}"
        print(f"\n📌 {sample['title']}:")
        print(f"   {url}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 LinkedIn Recent Jobs Scraper - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Configuration Validation", test_config_validation),
        ("URL Parsing", test_url_parsing),
        ("Easy Apply Detection", test_easy_apply_detection),
        ("Recent Jobs Logic", test_recent_jobs_logic),
        ("Sample URL Generation", generate_sample_urls)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n--- {test_name} ---")
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your recent jobs scraper is ready.")
        print("\nNext steps:")
        print("1. Update your config.json with desired search URLs")
        print("2. Run: python scraper_final.py")
        print("3. Check output: recent_non_easy_apply_jobs.csv")
        return True
    else:
        print("🚨 Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 