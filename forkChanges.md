LinkedIn Job Scraper Setup and Usage
Setup
1. Install Dependencies
Run the following command to install required dependencies:
pip install -r requirements.txt

2. Configure Authentication
This scraper requires authentication. Create a .env file in the root directory.
Cookie-based authentication is the recommended method to avoid CAPTCHA challenges.
Method 1: Cookie Authentication (Recommended)

Log in to LinkedIn.com in your browser.
Open Developer Tools (F12).
Go to the Application tab (Chrome) or Storage tab (Firefox).
Under Cookies > https://www.linkedin.com, find the cookie named li_at.
Copy its entire value.

Add the cookie to your .env file:
# Main authentication token. VERY long string.
LINKEDIN_LI_AT=AQEDARXxxxxxxxxxxxxxxxxxx...

Method 2: Credentials (Fallback)
If you do not use the cookie method, the script will fall back to using your email and password.
Add your credentials to the .env file:
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password

Usage
1. Configure Your Search
Edit the config.json file to define which jobs to search for. The scraper uses a list of URLs.
{
  "MAX_PAGES_PER_SEARCH": 3,
  "FILTER_EASY_APPLY": true,
  "SEARCH_URLS": [
    {
      "name": "Engineer Jobs - Last Hour",
      "url": "https://www.linkedin.com/jobs/search/?f_EA=false&f_TPR=r3600&geoId=101282230&keywords=engineer"
    },
    {
      "name": "Software Developer - Last 24h - USA",
      "url": "https://www.linkedin.com/jobs/search/?f_TPR=r86400&geoId=103644278&keywords=software%20developer"
    }
  ]
}

Build custom URLs using LinkedIn's search filters and paste them here.
Common URL parameters:

keywords: The job title. Use %20 for spaces (e.g., software%20engineer).
geoId: The location ID (e.g., 101282230 for Germany).
f_TPR: Time posted range (e.g., r3600 for last hour, r86400 for last 24 hours).
f_EA: Easy Apply filter (e.g., false to exclude Easy Apply jobs).

2. Run the Scraper
Execute the main script from your terminal:
python scraper_final.py

3. Check Results
The output is saved to recent_non_easy_apply_jobs.csv by default.