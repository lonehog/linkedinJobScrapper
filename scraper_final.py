#!/usr/bin/env python3
"""
LinkedIn Job Scraper – Synchronous Version with Randomly Generated Headers,
Enhanced Error Handling, Colorful & Structured Logging, and CSV Output

DESCRIPTION:
  This script scrapes job listings from LinkedIn for multiple search queries.
  All configuration values are loaded from a separate JSON file (by default config.json).
  If the JSON file is missing or incomplete (i.e. missing any required keys),
  the script logs an error message and exits to avoid any corrupt data.

  (See in-code comments and the accompanying config.json example for details.)

USAGE:
  - Create a valid config.json file in the same directory.
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
# 1. Configuration Class & Loader
# ------------------------------
class Config:
    # These values will be overwritten by the JSON configuration.
    BASE_LIST_URL = ""
    BASE_JOB_URL = ""
    NUM_JOBS_PER_QUERY = 0
    SEARCH_QUERIES = []
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
    """Load configuration from a JSON file and update the Config class.

    If the file is missing or incomplete, log an error and exit.
    """
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
        "NUM_JOBS_PER_QUERY",
        "SEARCH_QUERIES",
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
    Config.NUM_JOBS_PER_QUERY = config_data["NUM_JOBS_PER_QUERY"]
    Config.SEARCH_QUERIES = config_data["SEARCH_QUERIES"]
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
# 2. Functions for Random Header Generation
# ------------------------------
def generate_random_header():
    os_choice = random.choice([
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64"
    ])
    browser_choice = random.choice(["Chrome", "Firefox"])
    if browser_choice == "Chrome":
        version = f"{random.randint(90,115)}.0.{random.randint(3000,4000)}.{random.randint(100,200)}"
        ua = f"Mozilla/5.0 ({os_choice}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
    else:
        version = f"{random.randint(80,110)}.0"
        ua = f"Mozilla/5.0 ({os_choice}; rv:{version}) Gecko/20100101 Firefox/{version}"
    return {
        "User-Agent": ua,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

def add_random_headers(count: int):
    for _ in range(count):
        Config.HEADERS_LIST.append(generate_random_header())
    logger.info("Added %d additional random headers.", count)

def get_random_header():
    if not Config.HEADERS_LIST:
        add_random_headers(Config.INITIAL_HEADERS_COUNT)
    header = random.choice(Config.HEADERS_LIST)
    logger.info("Selected header: %s", header["User-Agent"])
    return header

# Initialize header pool after loading configuration.
# (This call will happen later in __main__ after loading the config.)

# ------------------------------
# 3. Fetch Job IDs for a Single Search Query
# ------------------------------
def fetch_job_ids(search_params: dict, num_jobs: int) -> list:
    log_separator("Starting Job ID Collection")
    logger.info("Query parameters: %s", search_params)
    id_list = []
    current_start = 0

    while len(id_list) < num_jobs:
        params = {**search_params, 'start': current_start}
        logger.debug("Requesting job IDs with parameters: %s", params)
        try:
            response = requests.get(
                Config.BASE_LIST_URL,
                params=params,
                headers=get_random_header(),
                timeout=Config.REQUEST_TIMEOUT
            )
        except requests.RequestException as e:
            logger.error("Error fetching job IDs at start=%d: %s", current_start, e)
            break

        if response.status_code == 429:
            logger.error("Received HTTP 429 Too Many Requests at start=%d.", current_start)
            logger.info("Waiting for %d seconds before retrying...", Config.RETRY_WAIT_429)
            time.sleep(Config.RETRY_WAIT_429)
            add_random_headers(Config.RANDOM_HEADERS_COUNT)
            continue
        elif response.status_code != 200:
            logger.error("Non-200 response at start=%d, status code: %d", current_start, response.status_code)
            logger.info("Waiting for %d seconds before retrying...", Config.RETRY_WAIT_NON_429)
            time.sleep(Config.RETRY_WAIT_NON_429)
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        new_ids = []
        for li in soup.find_all('li'):
            div = li.find('div', {'data-entity-urn': True})
            if div:
                job_id = div['data-entity-urn'].split(':')[-1]
                new_ids.append(job_id)

        if not new_ids:
            logger.info("No more job IDs found at start=%d.", current_start)
            break

        remaining = num_jobs - len(id_list)
        id_list.extend(new_ids[:remaining])
        logger.info("Collected %d job IDs so far.", len(id_list))
        current_start += 25
        time.sleep(Config.PAGE_DELAY)

    logger.info("Completed Job ID Collection. Total IDs: %d", len(id_list))
    return id_list

def fetch_job_details(job_id: str) -> dict:
    log_separator(f"Fetching Details for Job ID: {job_id}")
    url = Config.BASE_JOB_URL.format(job_id)
    attempts = 0
    max_attempts = Config.MAX_ATTEMPTS
    last_error = None

    while attempts < max_attempts:
        if attempts > 0:
            logger.info("Retrying job ID %s (Attempt %d of %d)", job_id, attempts + 1, max_attempts)
        if attempts == max_attempts - 1:
            logger.warning("Final attempt for job ID %s; adding %d additional headers.", job_id, Config.RANDOM_HEADERS_COUNT)
            add_random_headers(Config.RANDOM_HEADERS_COUNT)
        header = get_random_header()
        logger.info("Attempt %d for job ID %s using header: %s", attempts + 1, job_id, header["User-Agent"])
        try:
            response = requests.get(
                url,
                headers=header,
                timeout=Config.REQUEST_TIMEOUT
            )
        except requests.RequestException as e:
            last_error = f"RequestException on attempt {attempts+1}: {e}"
            logger.error("Error on attempt %d for job ID %s: %s", attempts + 1, job_id, e)
            response = None

        if response is not None:
            if response.status_code == 429:
                wait_time = Config.RETRY_WAIT_429 * (2 ** attempts)
                logger.error("HTTP 429 Too Many Requests for job ID %s on attempt %d.", job_id, attempts + 1)
                logger.info("Waiting for %d seconds before retrying.", wait_time)
                time.sleep(wait_time)
            elif response.status_code != 200:
                logger.error("HTTP error on attempt %d for job ID %s: status code %d", attempts + 1, job_id, response.status_code)
                logger.info("Waiting for %d seconds before retrying...", Config.RETRY_WAIT_NON_429)
                time.sleep(Config.RETRY_WAIT_NON_429)
            else:
                logger.info("Successfully fetched details for job ID %s on attempt %d.", job_id, attempts + 1)
                soup = BeautifulSoup(response.text, 'html.parser')
                job = {"job_id": job_id, "job_url": f"https://www.linkedin.com/jobs/view/{job_id}"}

                primary_components = {
                    'company_name': ('a', 'topcard__org-name-link'),
                    'time_posted': ('span', 'posted-time-ago__text'),
                    'num_applicants': ('span', 'num-applicants__caption'),
                    'job_title': ('h2', 'topcard__title')
                }
                for key, (tag, css_class) in primary_components.items():
                    element = soup.find(tag, class_=css_class)
                    job[key] = element.get_text(strip=True) if element else 'N/A'
                    logger.debug("Extracted %s: %s", key, job[key])

                description_div = soup.find('div', class_='description__text')
                job['description_content'] = description_div.get_text(strip=True) if description_div else 'N/A'
                logger.debug("Extracted job description.")

                experience_span = soup.find('span', class_='experience')
                if experience_span:
                    job['experience_needed'] = experience_span.get_text(strip=True)
                else:
                    desc_text = job['description_content'].lower() if job['description_content'] != 'N/A' else ''
                    if "experience" in desc_text:
                        start_index = desc_text.find("experience")
                        job['experience_needed'] = job['description_content'][start_index:start_index + 100] + "..."
                    else:
                        job['experience_needed'] = 'N/A'
                logger.debug("Extracted experience needed: %s", job['experience_needed'])

                structured_data = soup.find('script', type='application/ld+json')
                if structured_data:
                    try:
                        job_json = json.loads(structured_data.string)
                        if isinstance(job_json, list):
                            job_json = job_json[0]
                        if 'jobLocation' in job_json:
                            loc = job_json['jobLocation']
                            if isinstance(loc, list):
                                loc = loc[0]
                            if 'address' in loc and isinstance(loc['address'], dict):
                                job['job_location'] = loc['address'].get('addressLocality', 'N/A')
                            else:
                                job['job_location'] = 'N/A'
                        else:
                            job['job_location'] = 'N/A'
                        logger.debug("Extracted job location: %s", job['job_location'])
                        job['date_posted'] = job_json.get('datePosted', 'N/A')
                        logger.debug("Extracted date posted: %s", job['date_posted'])
                    except Exception as e:
                        last_error = f"Error parsing JSON-LD: {e}"
                        logger.error("Error parsing JSON-LD for job ID %s: %s", job_id, e)
                        job['job_location'] = 'N/A'
                        job['date_posted'] = 'N/A'
                else:
                    loc_elem = soup.find('span', class_='topcard__flavor--bullet')
                    job['job_location'] = loc_elem.get_text(strip=True) if loc_elem else 'N/A'
                    logger.debug("Extracted fallback job location: %s", job['job_location'])
                    job['date_posted'] = 'N/A'
                    logger.debug("No JSON-LD found; setting date posted to N/A.")

                return job

        attempts += 1

    logger.error("Failed to fetch details for job ID %s after %d attempts. Last error: %s", job_id, max_attempts, last_error)
    return {}
# ------------------------------
# 5. Main: Process All Queries and Save CSV Output
# ------------------------------
def main():
    log_separator("Starting Scraping Process")

    # Initialize the header pool now that the configuration is loaded.
    add_random_headers(Config.INITIAL_HEADERS_COUNT)
    logger.info("Initialized header pool with %d headers.", len(Config.HEADERS_LIST))

    all_job_data = []
    overall_monitoring = []
    total_duplicates = 0

    logger.info("Processing %d queries.", len(Config.SEARCH_QUERIES))
    for query in Config.SEARCH_QUERIES:
        log_separator(f"Processing Query: {query.get('keywords', 'N/A')} in {query.get('location', 'N/A')}")
        logger.info("Query parameters: %s", query)
        job_ids = fetch_job_ids(query, Config.NUM_JOBS_PER_QUERY)
        query_monitoring = {
            "keywords": query.get('keywords', 'N/A'),
            "location": query.get('location', 'N/A'),
            "jobs_found": len(job_ids)
        }
        unique_ids = set()

        for job_id in job_ids:
            if job_id in unique_ids:
                total_duplicates += 1
                continue
            job_detail = fetch_job_details(job_id)
            if job_detail:
                all_job_data.append(job_detail)
                unique_ids.add(job_id)

        query_monitoring["unique_jobs"] = len(unique_ids)
        overall_monitoring.append(query_monitoring)
        logger.info("Query '%s': Collected %d job IDs, %d unique jobs.",
                    query_monitoring["keywords"], query_monitoring["jobs_found"], query_monitoring["unique_jobs"])

    df = pd.DataFrame(all_job_data)
    df = df[Config.OUTPUT_FIELDS]
    df.to_csv(Config.CSV_FILENAME, index=False)
    logger.info("Saved job details to CSV file '%s'.", Config.CSV_FILENAME)

    log_separator("Scraping Summary")
    for monitor in overall_monitoring:
        logger.info("Query '%s' in %s: %d job IDs, %d unique jobs.",
                    monitor['keywords'], monitor['location'], monitor['jobs_found'], monitor['unique_jobs'])
    total_unique = df['job_id'].nunique()
    logger.info("Total unique jobs scraped (union across queries): %d", total_unique)
    logger.info("Total duplicate job IDs skipped: %d", total_duplicates)

    print("\n--- Scraping Summary ---")
    for monitor in overall_monitoring:
        print(f"Query '{monitor['keywords']}' in {monitor['location']}: "
              f"Found {monitor['jobs_found']} job IDs, {monitor['unique_jobs']} unique jobs.")
    print(f"\nTotal unique jobs scraped (union across queries): {total_unique}")
    print(f"Total duplicate job IDs skipped: {total_duplicates}")
    print("\nNote: The total unique jobs is the union of all jobs scraped across queries; "
          "duplicates are removed if a job appears in more than one query.")

# ------------------------------
# 6. Execution Entry Point
# ------------------------------
if __name__ == "__main__":
    # Load configuration from the external JSON file.
    load_config_from_json("config.json")
    main()
