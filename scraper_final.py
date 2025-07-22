#!/usr/bin/env python3
"""
LinkedIn Job Scraper – URL-Based Recent Jobs (Last Hour)

DESCRIPTION:
  This script scrapes recent job listings from LinkedIn using specific search URLs.
  It focuses on jobs posted in the last hour (f_TPR=3600) and collects all jobs
  regardless of Easy Apply status. LinkedIn credentials are loaded from environment 
  variables for authentication.

USAGE:
  - Create a valid config.json file with SEARCH_URLS.
  - Create a .env file with LINKEDIN_EMAIL and LINKEDIN_PASSWORD.
  - Run this script in your Python environment.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import random
import time
import logging
import sys
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, urlencode
import re

# Load environment variables from .env file
load_dotenv()

# ------------------------------
# 0. Colored Logging Configuration
# ------------------------------

# ANSI escape sequences for colors.
LOG_COLORS = {
    'DEBUG': "\033[36m",    # Cyan
    'INFO': "\033[32m",     # Green
    'WARNING': "\033[33m",  # Yellow
    'ERROR': "\033[31m",    # Red
    'CRITICAL': "\033[41m", # Red background
    'RESET': "\033[0m"
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages based on level."""
    def format(self, record):
        levelname = record.levelname
        if levelname in LOG_COLORS:
            record.levelname = f"{LOG_COLORS[levelname]}{levelname}{LOG_COLORS['RESET']}"
        return super().format(record)

console_handler = logging.StreamHandler()
formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(console_handler)
else:
    logger.handlers = [console_handler]

def log_separator(message: str):
    """Log a separator line with a centered message."""
    sep = "-" * 80
    logger.info("\n%s\n%s\n%s", sep, message.center(80), sep)

# ------------------------------
# 1. LinkedIn Authentication Class
# ------------------------------
class LinkedInAuth:
    """Handles LinkedIn authentication and session management."""
    
    def __init__(self):
        self.session = requests.Session()
        self.is_authenticated = False
        self.csrf_token = None
        
    def get_credentials(self):
        """Load LinkedIn credentials from environment variables."""
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            logger.error("LinkedIn credentials not found in environment variables.")
            logger.error("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in your .env file.")
            sys.exit(1)
            
        return email, password
    
    def get_session_cookies(self):
        """Load LinkedIn session cookies from environment variables."""
        cookies = {
            'li_at': os.getenv('LINKEDIN_LI_AT'),
            'JSESSIONID': os.getenv('LINKEDIN_JSESSIONID'),
            'liap': os.getenv('LINKEDIN_LIAP'),
            'lidc': os.getenv('LINKEDIN_LIDC'),
            'bcookie': os.getenv('LINKEDIN_BCOOKIE'),
            'bscookie': os.getenv('LINKEDIN_BSCOOKIE')
        }
        
        # Filter out None values
        return {k: v for k, v in cookies.items() if v is not None}
    
    def login_with_cookies(self):
        """Authenticate using pre-exported session cookies (bypasses CAPTCHA)."""
        log_separator("LinkedIn Cookie Authentication")
        
        cookies = self.get_session_cookies()
        
        if not cookies.get('li_at'):
            logger.warning("LINKEDIN_LI_AT cookie not found. Cookie authentication unavailable.")
            return False
            
        logger.info("Using pre-authenticated session cookies...")
        
        try:
            # Set cookies in session
            for name, value in cookies.items():
                if value:
                    self.session.cookies.set(name, value, domain='.linkedin.com')
                    logger.debug("Set cookie: %s", name)
            
            # Verify authentication by checking a protected page
            logger.info("Verifying cookie authentication...")
            test_url = "https://www.linkedin.com/feed/"
            headers = self.get_authenticated_headers()
            
            response = self.session.get(test_url, headers=headers, timeout=30, allow_redirects=True)
            
            if self.verify_authentication(response):
                logger.info("✅ Cookie-based authentication successful!")
                self.is_authenticated = True
                return True
            else:
                logger.warning("❌ Cookie authentication failed - cookies may be expired")
                logger.warning("Response URL: %s", response.url)
                return False
                
        except Exception as e:
            logger.error("Cookie authentication error: %s", e)
            return False
    
    def login(self):
        """Authenticate with LinkedIn - tries cookies first, then credentials."""
        log_separator("LinkedIn Authentication")
        
        # Try cookie-based authentication first (bypasses CAPTCHA)
        logger.info("Attempting cookie-based authentication...")
        if self.login_with_cookies():
            return True
            
        logger.info("Cookie authentication failed or unavailable, trying credential login...")
        
        email, password = self.get_credentials()
        logger.info("Starting LinkedIn credential authentication process...")
        
        try:
            # Step 1: Get login page to extract CSRF token
            logger.info("Fetching login page...")
            login_url = "https://www.linkedin.com/login"
            
            headers = self.get_login_headers()
            response = self.session.get(login_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error("Failed to access LinkedIn login page. Status: %d", response.status_code)
                return False
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract CSRF token
            csrf_input = soup.find('input', {'name': 'loginCsrfParam'})
            if not csrf_input:
                logger.error("Could not find CSRF token on login page")
                return False
                
            self.csrf_token = csrf_input.get('value')
            logger.info("Successfully extracted CSRF token")
            
            # Step 2: Submit login credentials
            logger.info("Submitting login credentials...")
            
            login_data = {
                'session_key': email,
                'session_password': password,
                'loginCsrfParam': self.csrf_token,
                'trk': 'guest_homepage-basic_sign-in-submit'
            }
            
            login_submit_url = "https://www.linkedin.com/checkpoint/lg/login-submit"
            
            # Add delay to mimic human behavior
            time.sleep(random.uniform(2, 4))
            
            response = self.session.post(
                login_submit_url,
                data=login_data,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            # Check if login was successful
            if self.verify_authentication(response):
                logger.info("✅ LinkedIn authentication successful!")
                self.is_authenticated = True
                return True
            else:
                logger.error("❌ LinkedIn authentication failed")
                self.handle_auth_failure(response)
                return False
                
        except requests.RequestException as e:
            logger.error("Network error during authentication: %s", e)
            return False
        except Exception as e:
            logger.error("Unexpected error during authentication: %s", e)
            return False
    
    def verify_authentication(self, response):
        """Verify if authentication was successful."""
        logger.debug("Verifying authentication - Response URL: %s", response.url)
        logger.debug("Response Status Code: %d", response.status_code)
        
        # Check for successful URL indicators
        if 'feed' in response.url or 'mynetwork' in response.url or 'linkedin.com/in/' in response.url:
            logger.debug("✅ Authentication verified by URL pattern")
            return True
            
        # Check if we're redirected to LinkedIn home
        if 'linkedin.com/feed' in response.url:
            logger.debug("✅ Authentication verified by feed redirect")
            return True
            
        # Check response content for authentication indicators
        if 'JSESSIONID' in str(response.cookies) or 'li_at' in str(response.cookies):
            logger.debug("✅ Authentication verified by session cookies")
            return True
            
        # Look for specific elements that indicate successful login
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for authenticated navigation elements
        nav_indicators = [
            'nav.global-nav',
            '.global-nav',
            '[data-test-id="nav-user-menu"]',
            '.nav-user-menu',
            '.feed-container',
            '.authentication-outlet'
        ]
        
        for selector in nav_indicators:
            if soup.select(selector):
                logger.debug("✅ Authentication verified by page element: %s", selector)
                return True
        
        # Additional check for LinkedIn authenticated pages
        if response.status_code == 200 and 'LinkedIn' in response.text and 'sign in' not in response.text.lower():
            # Check if we're not on login/guest pages
            if not any(keyword in response.url for keyword in ['login', 'guest', 'authwall', 'signup']):
                logger.debug("✅ Authentication likely successful - authenticated page detected")
                return True
        
        logger.debug("❌ Authentication verification failed")
        return False
    
    def handle_auth_failure(self, response):
        """Handle authentication failure and provide helpful feedback."""
        if 'challenge' in response.url:
            logger.error("LinkedIn requires additional verification (CAPTCHA/2FA)")
            logger.error("Please log in manually through a browser first")
        elif 'checkpoint' in response.url:
            logger.error("LinkedIn security checkpoint detected")
            logger.error("Your account may be flagged for suspicious activity")
        elif response.status_code == 401:
            logger.error("Invalid credentials provided")
        else:
            logger.error("Authentication failed for unknown reason")
            logger.error("Response URL: %s", response.url)
            logger.error("Status Code: %d", response.status_code)
    
    def get_login_headers(self):
        """Get realistic headers for login requests."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def get_authenticated_headers(self):
        """Get headers for authenticated requests."""
        base_header = generate_random_header()
        base_header.update({
            'X-Requested-With': 'XMLHttpRequest',
            'X-LI-Lang': 'en_US',
            'Accept': 'application/vnd.linkedin.normalized+json+2.1',
            'csrf-token': self.csrf_token if self.csrf_token else ''
        })
        return base_header

# Global authentication instance
linkedin_auth = LinkedInAuth()

# ------------------------------
# 2. Configuration Class & Loader
# ------------------------------
class Config:
    # These values will be overwritten by the JSON configuration.
    BASE_LIST_URL = ""
    BASE_JOB_URL = ""
    MAX_PAGES_PER_SEARCH = 0
    FILTER_EASY_APPLY = False
    SEARCH_URLS = []
    REQUEST_TIMEOUT = 0
    PAGE_DELAY = 0
    CSV_FILENAME = ""
    INITIAL_HEADERS_COUNT = 0
    RANDOM_HEADERS_COUNT = 0
    MAX_ATTEMPTS = 0
    RETRY_WAIT_429 = 0
    RETRY_WAIT_NON_429 = 0
    OUTPUT_FIELDS = []
    HEADERS_LIST = []  # This list will be used to store generated headers.

def load_config_from_json(file_path: str):
    """Load configuration from a JSON file and update the Config class."""
    if not os.path.exists(file_path):
        logger.error("JSON file missing")
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Error parsing JSON file: %s", e)
        sys.exit(1)

    # List of required keys in the JSON configuration.
    required_keys = [
        "BASE_LIST_URL",
        "BASE_JOB_URL",
        "MAX_PAGES_PER_SEARCH",
        "FILTER_EASY_APPLY",
        "SEARCH_URLS",
        "REQUEST_TIMEOUT",
        "PAGE_DELAY",
        "CSV_FILENAME",
        "INITIAL_HEADERS_COUNT",
        "RANDOM_HEADERS_COUNT",
        "MAX_ATTEMPTS",
        "RETRY_WAIT_429",
        "RETRY_WAIT_NON_429",
        "OUTPUT_FIELDS"
    ]
    missing_keys = [key for key in required_keys if key not in config_data]
    if missing_keys:
        logger.error("JSON file incomplete, missing keys: %s", ', '.join(missing_keys))
        sys.exit(1)

    # Update the Config class attributes.
    Config.BASE_LIST_URL = config_data["BASE_LIST_URL"]
    Config.BASE_JOB_URL = config_data["BASE_JOB_URL"]
    Config.MAX_PAGES_PER_SEARCH = config_data["MAX_PAGES_PER_SEARCH"]
    Config.FILTER_EASY_APPLY = config_data["FILTER_EASY_APPLY"]
    Config.SEARCH_URLS = config_data["SEARCH_URLS"]
    Config.REQUEST_TIMEOUT = config_data["REQUEST_TIMEOUT"]
    Config.PAGE_DELAY = config_data["PAGE_DELAY"]
    Config.CSV_FILENAME = config_data["CSV_FILENAME"]
    Config.INITIAL_HEADERS_COUNT = config_data["INITIAL_HEADERS_COUNT"]
    Config.RANDOM_HEADERS_COUNT = config_data["RANDOM_HEADERS_COUNT"]
    Config.MAX_ATTEMPTS = config_data["MAX_ATTEMPTS"]
    Config.RETRY_WAIT_429 = config_data["RETRY_WAIT_429"]
    Config.RETRY_WAIT_NON_429 = config_data["RETRY_WAIT_NON_429"]
    Config.OUTPUT_FIELDS = config_data["OUTPUT_FIELDS"]

# ------------------------------
# 3. Functions for Random Header Generation
# ------------------------------
def generate_random_header():
    os_choice = random.choice([
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64"
    ])
    browser_choice = random.choice(["Chrome", "Firefox"])
    if browser_choice == "Chrome":
        version = f"{random.randint(115,125)}.0.{random.randint(3000,6000)}.{random.randint(100,300)}"
        ua = f"Mozilla/5.0 ({os_choice}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
    else:
        version = f"{random.randint(110,125)}.0"
        ua = f"Mozilla/5.0 ({os_choice}; rv:{version}) Gecko/20100101 Firefox/{version}"
    return {
        "User-Agent": ua,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def add_random_headers(count: int):
    for _ in range(count):
        Config.HEADERS_LIST.append(generate_random_header())
    logger.info("Added %d additional random headers.", count)

def get_random_header():
    if not Config.HEADERS_LIST:
        add_random_headers(Config.INITIAL_HEADERS_COUNT)
    header = random.choice(Config.HEADERS_LIST)
    logger.debug("Selected header: %s", header["User-Agent"])
    return header

# ------------------------------
# 4. Authenticated Request Functions
# ------------------------------
def make_authenticated_request(url, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            logger.debug(f"Requesting URL: {url} with headers: {headers}")
            
            response = requests.get(url, params=params, headers=headers, timeout=10, allow_redirects=True)
            
            logger.debug(f"Response status: {response.status_code}, URL: {response.url}")
            
            if response.status_code == 429:  # Too Many Requests
                wait_time = 10 * (2 ** attempt)
                logger.error(f"HTTP 429: Too Many Requests. Waiting {wait_time} seconds.")
                time.sleep(wait_time)
                continue
            
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code} for URL: {response.url}")
                time.sleep(5)
                continue
            
            return response
            
        except requests.RequestException as e:
            logger.error(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))
    
    logger.error(f"All retries failed for URL: {url}")
    return None

# ------------------------------
# 5. Easy Apply Detection Functions
# ------------------------------
def detect_easy_apply(job_element):
    """Detect if a job has Easy Apply option."""
    # Look for Easy Apply indicators in the job card
    easy_apply_indicators = [
        'Easy Apply',
        'easy-apply',
        'apply-button--primary',
        'jobs-apply-button--top-card',
        'artdeco-button--primary'
    ]
    
    job_html = str(job_element)
    for indicator in easy_apply_indicators:
        if indicator.lower() in job_html.lower():
            return True
    
    # Check for specific Easy Apply elements
    easy_apply_elements = job_element.find_all(['button', 'span', 'div'], 
                                             string=re.compile(r'Easy Apply', re.IGNORECASE))
    if easy_apply_elements:
        return True
    
    # Check for non-Easy Apply indicators
    external_apply_indicators = [
        'Be an early applicant',
        'Apply on company website',
        'Apply externally'
    ]
    
    for indicator in external_apply_indicators:
        if indicator.lower() in job_html.lower():
            return False
    
    return False

def get_application_type(job_element):
    """Determine the application type for a job."""
    if detect_easy_apply(job_element):
        return "Easy Apply"
    
    # Check for external application indicators
    job_html = str(job_element).lower()
    
    if 'be an early applicant' in job_html:
        return "Early Applicant"
    elif 'apply on company website' in job_html:
        return "Company Website"
    elif 'apply externally' in job_html:
        return "External"
    else:
        return "Standard"

# ------------------------------
# 6. Fetch Job IDs from URL-Based Search
# ------------------------------
def fetch_job_ids_from_url(search_url_config: dict) -> list:
    """Fetch job IDs from a specific LinkedIn search URL."""
    log_separator(f"Starting Job ID Collection: {search_url_config['name']}")
    logger.info("Search URL: %s", search_url_config['url'])
    
    id_list = []
    all_jobs = []
    page = 0
    max_pages = Config.MAX_PAGES_PER_SEARCH
    
    while page < max_pages:
        # Parse the URL and add start parameter for pagination
        parsed_url = urlparse(search_url_config['url'])
        query_params = parse_qs(parsed_url.query)
        
        # Add pagination parameter
        query_params['start'] = [str(page * 25)]
        
        # Reconstruct URL
        new_query = urlencode(query_params, doseq=True)
        paginated_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"
        
        logger.info("Fetching page %d: %s", page + 1, paginated_url)
        
        response = make_authenticated_request(paginated_url)
        
        if not response:
            logger.error("Failed to get response for page %d", page + 1)
            break

        if response.status_code == 429:
            logger.error("Received HTTP 429 Too Many Requests on page %d.", page + 1)
            logger.info("Waiting for %d seconds before retrying...", Config.RETRY_WAIT_429)
            time.sleep(Config.RETRY_WAIT_429)
            add_random_headers(Config.RANDOM_HEADERS_COUNT)
            continue
        elif response.status_code != 200:
            logger.error("Non-200 response on page %d, status code: %d", page + 1, response.status_code)
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find job cards
        job_cards = soup.find_all(['div', 'li'], {'data-entity-urn': True})
        if not job_cards:
            # Fallback: look for job links
            job_links = soup.find_all('a', href=re.compile(r'/jobs/view/\d+'))
            for link in job_links:
                href = link.get('href')
                job_id_match = re.search(r'/jobs/view/(\d+)', href)
                if job_id_match:
                    job_id = job_id_match.group(1)
                    
                    # Find the parent job card for Easy Apply detection
                    job_card = link.find_parent(['div', 'li'], class_=re.compile(r'job|result'))
                    if job_card:
                        has_easy_apply = detect_easy_apply(job_card)
                        app_type = get_application_type(job_card)
                        all_jobs.append({
                                'job_id': job_id,
                                'has_easy_apply': has_easy_apply,
                                'application_type': app_type
                            })
        else:
            for card in job_cards:
                entity_urn = card.get('data-entity-urn', '')
                if 'job' in entity_urn.lower():
                    job_id = entity_urn.split(':')[-1]
                    if job_id.isdigit():
                        has_easy_apply = detect_easy_apply(card)
                        app_type = get_application_type(card)
                        all_jobs.append({
                                'job_id': job_id,
                                'has_easy_apply': has_easy_apply,
                                'application_type': app_type
                            })


        if not job_cards and not job_links:
            logger.info("No more jobs found on page %d.", page + 1)
            break

        logger.info("Page %d: Found %d jobs so far", page + 1, len(all_jobs))
        page += 1
        
        # Respectful delay between pages
        time.sleep(Config.PAGE_DELAY)

    logger.info("Completed search '%s'. Total jobs: %d", 
                search_url_config['name'], len(all_jobs))
    return all_jobs

def fetch_job_details(job_info: dict) -> dict:
    """Fetch detailed information for a specific job."""
    job_id = job_info['job_id']
    log_separator(f"Fetching Details for Job ID: {job_id}")
    
    # Use authenticated job detail URL
    url = f"https://www.linkedin.com/jobs/view/{job_id}/"
    attempts = 0
    max_attempts = Config.MAX_ATTEMPTS
    last_error = None

    while attempts < max_attempts:
        if attempts > 0:
            logger.info("Retrying job ID %s (Attempt %d of %d)", job_id, attempts + 1, max_attempts)
        
        logger.info("Attempt %d for job ID %s", attempts + 1, job_id)
        
        response = make_authenticated_request(url)
        
        if not response:
            last_error = f"Failed to get response on attempt {attempts+1}"
            logger.error("Failed to get response for job ID %s on attempt %d", job_id, attempts + 1)
        elif response.status_code == 429:
            wait_time = Config.RETRY_WAIT_429 * (2 ** attempts)
            logger.error("HTTP 429 Too Many Requests for job ID %s on attempt %d.", job_id, attempts + 1)
            logger.info("Waiting for %d seconds before retrying.", wait_time)
            time.sleep(wait_time)
        elif response.status_code == 404:
            logger.warning("Job ID %s not found (404). Job may have been removed.", job_id)
            return {}
        elif response.status_code != 200:
            logger.error("HTTP error on attempt %d for job ID %s: status code %d", attempts + 1, job_id, response.status_code)
            logger.info("Waiting for %d seconds before retrying...", Config.RETRY_WAIT_NON_429)
            time.sleep(Config.RETRY_WAIT_NON_429)
        else:
            logger.info("Successfully fetched details for job ID %s on attempt %d.", job_id, attempts + 1)
            soup = BeautifulSoup(response.text, 'html.parser')
            job = {
                "job_id": job_id, 
                "job_url": f"https://www.linkedin.com/jobs/view/{job_id}",
                "has_easy_apply": job_info.get('has_easy_apply', False),
                "application_type": job_info.get('application_type', 'Unknown')
            }

            # Updated selectors for authenticated LinkedIn interface
            selectors = {
                'company_name': [
                    '.job-details-jobs-unified-top-card__company-name a',
                    '.jobs-unified-top-card__company-name a',
                    '.topcard__org-name-link',
                    'a[data-tracking-control-name="job_details_topcard_company_url"]'
                ],
                'job_title': [
                    '.job-details-jobs-unified-top-card__job-title h1',
                    '.jobs-unified-top-card__job-title h1',
                    '.topcard__title',
                    'h1.jobs-unified-top-card__job-title'
                ],
                'time_posted': [
                    '.job-details-jobs-unified-top-card__primary-description-container .tvm__text',
                    '.jobs-unified-top-card__subtitle .tvm__text',
                    '.posted-time-ago__text',
                    'span[data-tracking-control-name="job_details_topcard_posted_time"]'
                ],
                'num_applicants': [
                    '.job-details-jobs-unified-top-card__primary-description-container .tvm__text--low-emphasis',
                    '.jobs-unified-top-card__subtitle .tvm__text--low-emphasis',
                    '.num-applicants__caption'
                ],
                'job_location': [
                    '.job-details-jobs-unified-top-card__primary-description-container .tvm__text--neutral',
                    '.jobs-unified-top-card__bullet',
                    '.topcard__flavor--bullet'
                ]
            }

            # Extract job details using multiple selectors
            for key, selector_list in selectors.items():
                job[key] = 'N/A'
                for selector in selector_list:
                    element = soup.select_one(selector)
                    if element:
                        job[key] = element.get_text(strip=True)
                        break
                logger.debug("Extracted %s: %s", key, job[key])

            # Extract job description
            description_selectors = [
                '.jobs-description-content__text',
                '.jobs-box__html-content',
                '.description__text',
                '.jobs-description__content'
            ]
            
            job['description_content'] = 'N/A'
            for selector in description_selectors:
                desc_div = soup.select_one(selector)
                if desc_div:
                    job['description_content'] = desc_div.get_text(strip=True)
                    break
            logger.debug("Extracted job description.")

            # Extract experience requirements
            experience_keywords = ['experience', 'years', 'level', 'senior', 'junior', 'entry']
            job['experience_needed'] = 'N/A'
            
            if job['description_content'] != 'N/A':
                desc_text = job['description_content'].lower()
                for keyword in experience_keywords:
                    if keyword in desc_text:
                        start_idx = desc_text.find(keyword)
                        # Extract context around the keyword
                        context_start = max(0, start_idx - 50)
                        context_end = min(len(job['description_content']), start_idx + 150)
                        job['experience_needed'] = job['description_content'][context_start:context_end].strip() + "..."
                        break

            logger.debug("Extracted experience needed: %s", job['experience_needed'])
            return job

        attempts += 1

    logger.error("Failed to fetch details for job ID %s after %d attempts. Last error: %s", job_id, max_attempts, last_error)
    return {}

# ------------------------------
# 7. Main: Process All URL Searches and Save CSV Output
# ------------------------------
def main():
    log_separator("Starting LinkedIn Recent Jobs Scraper with Easy Apply Filtering")
    
    # Authenticate with LinkedIn first
    if not linkedin_auth.login():
        logger.error("Failed to authenticate with LinkedIn. Exiting.")
        sys.exit(1)
    
    # Initialize the header pool
    add_random_headers(Config.INITIAL_HEADERS_COUNT)
    logger.info("Initialized header pool with %d headers.", len(Config.HEADERS_LIST))

    all_job_data = []
    overall_monitoring = []
    total_easy_apply_filtered = 0

    logger.info("Processing %d search URLs.", len(Config.SEARCH_URLS))
    for search_config in Config.SEARCH_URLS:
        log_separator(f"Processing Search: {search_config['name']}")
        logger.info("Description: %s", search_config.get('description', 'N/A'))
        
        job_info_list = fetch_job_ids_from_url(search_config)
        search_monitoring = {
            "name": search_config['name'],
            "jobs_found": len(job_info_list),
            "filter_applied": Config.FILTER_EASY_APPLY
        }
        
        unique_jobs = set()
        
        for job_info in job_info_list:
            job_id = job_info['job_id']
            if job_id in unique_jobs:
                continue
                
            job_detail = fetch_job_details(job_info)
            if job_detail:
                all_job_data.append(job_detail)
                unique_jobs.add(job_id)

        search_monitoring["unique_jobs"] = len(unique_jobs)
        overall_monitoring.append(search_monitoring)
        logger.info("Search '%s': Found %d jobs, %d unique jobs.",
                    search_monitoring["name"], search_monitoring["jobs_found"], search_monitoring["unique_jobs"])

    if all_job_data:
        df = pd.DataFrame(all_job_data)
        # Ensure all configured fields are present
        for field in Config.OUTPUT_FIELDS:
            if field not in df.columns:
                df[field] = 'N/A'
        
        df = df[Config.OUTPUT_FIELDS]
        df.to_csv(Config.CSV_FILENAME, index=False)
        logger.info("Saved job details to CSV file '%s'.", Config.CSV_FILENAME)
    else:
        logger.warning("No job data collected. CSV file not created.")

    log_separator("Scraping Summary")
    for monitor in overall_monitoring:
        logger.info("Search '%s': %d jobs found, %d unique jobs saved.",
                    monitor['name'], monitor['jobs_found'], monitor['unique_jobs'])
    
    if all_job_data:
        total_unique = len(set(job['job_id'] for job in all_job_data))
        logger.info("Total unique jobs scraped: %d", total_unique)
        
        # Count Easy Apply vs Non-Easy Apply
        easy_apply_count = sum(1 for job in all_job_data if job.get('has_easy_apply', False))
        non_easy_apply_count = total_unique - easy_apply_count
        
        print("\n--- Recent Jobs Scraping Summary (Last Hour) ---")
        for monitor in overall_monitoring:
            print(f"Search '{monitor['name']}': "
                  f"Found {monitor['jobs_found']} jobs, {monitor['unique_jobs']} unique jobs.")
        print(f"\nTotal unique jobs scraped: {total_unique}")
        print(f"- Easy Apply jobs: {easy_apply_count}")
        print(f"- Non-Easy Apply jobs: {non_easy_apply_count}")
        print(f"Pages per search: {Config.MAX_PAGES_PER_SEARCH}")
        print(f"Output file: {Config.CSV_FILENAME}")
    else:
        print("\n--- No Jobs Found ---")
        print("No job data was collected from the last hour. Try adjusting your search URLs or check if there are recent job postings.")

# ------------------------------
# 8. Execution Entry Point
# ------------------------------
if __name__ == "__main__":
    # Load configuration from the external JSON file.
    load_config_from_json("config.json")
    main()
