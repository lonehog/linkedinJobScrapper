# LinkedIn Job Scraper API

A Docker-based API server for scraping LinkedIn job listings. This application converts job search results into JSON format instead of CSV files, making it perfect for integration with other applications.

⚠️ Disclaimer
This project is intended for educational purposes only. The use of web scraping to collect data from LinkedIn or any other website may violate the terms of service of those websites. Please ensure that you have the necessary permissions and comply with all applicable laws and regulations before using this scraper. The authors of this project are not responsible for any misuse or legal consequences resulting from the use of this tool.

## Features

- **RESTful API**: Easy-to-use HTTP endpoints for job scraping
- **Docker-based**: Runs in Ubuntu containers for consistency
- **JSON Output**: Returns structured JSON data instead of CSV files
- **Configurable**: Support for custom search parameters
- **Authentication**: Supports both LinkedIn credentials and session cookies
- **Rate Limiting**: Built-in delays and retry logic to respect LinkedIn's limits

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd n8n_linkedinJobScrapper
```

### 2. Configure Environment

Copy the example environment file and fill in your LinkedIn credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your LinkedIn credentials (see Authentication section below).

### 3. Build and Run with Docker

```bash
# Build and start the API server
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

The API will be available at `http://localhost:8000`

## Authentication Methods

### Method 1: Username/Password
Add your LinkedIn credentials to `.env`:
```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

⚠️ **Warning**: This method may trigger CAPTCHA challenges.

### Method 2: Session Cookies (Recommended)
1. Log into LinkedIn in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage > Cookies > https://www.linkedin.com
4. Copy these cookie values to your `.env` file:
   - `li_at`
   - `JSESSIONID` 
   - `liap`
   - `lidc`
   - `bcookie`
   - `bscookie`

## API Endpoints

### Health Check
```http
GET /health
```

### Default Job Scraping
```http
GET /jobs
```
Scrapes jobs using the configuration from `config.json`.

### Custom Job Scraping
```http
POST /jobs/custom
Content-Type: application/json

{
  "search_urls": [
    {
      "name": "Python Jobs",
      "url": "https://www.linkedin.com/jobs/search/?keywords=python&location=...",
      "description": "Python developer jobs"
    }
  ],
  "max_pages": 2,
  "filter_easy_apply": true
}
```

### Search Jobs with Parameters
```http
GET /jobs/search?keywords=python&location=101282230&experience_level=2&time_filter=r3600&max_pages=1
```

**Parameters:**
- `keywords`: Job search keywords (required)
- `location`: LinkedIn location ID (default: 101282230 - India)
- `experience_level`: 1=Internship, 2=Entry level, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive
- `time_filter`: r3600=1h, r86400=24h, r604800=1w
- `max_pages`: Maximum pages to scrape

## Response Format

All job endpoints return JSON in this format:

```json
{
  "success": true,
  "message": "Successfully scraped 15 jobs",
  "jobs": [
    {
      "job_id": "3775423847",
      "job_url": "https://www.linkedin.com/jobs/view/3775423847",
      "company_name": "TechCorp",
      "job_title": "Software Engineer",
      "time_posted": "1 hour ago",
      "num_applicants": "50 applicants",
      "job_location": "San Francisco, CA",
      "experience_needed": "2+ years experience in...",
      "description_content": "We are looking for...",
      "has_easy_apply": true,
      "application_type": "Easy Apply"
    }
  ],
  "total_jobs": 15,
  "timestamp": "2024-01-15T10:30:00"
}
```

## Configuration

Edit `config.json` to customize default search parameters:

```json
{
  "MAX_PAGES_PER_SEARCH": 1,
  "SEARCH_URLS": [
    {
      "name": "Firmware Jobs - Last Hour",
      "url": "https://www.linkedin.com/jobs/search/?f_E=2&f_TPR=r3600&keywords=firmware",
      "description": "Firmware jobs posted in last hour"
    }
  ],
  "REQUEST_TIMEOUT": 30,
  "PAGE_DELAY": 10
}
```

## Usage Examples

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get jobs with default config
curl http://localhost:8000/jobs

# Search for specific jobs
curl "http://localhost:8000/jobs/search?keywords=python&max_pages=2"
```

### Using Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Get jobs
response = requests.get("http://localhost:8000/jobs")
jobs_data = response.json()

print(f"Found {jobs_data['total_jobs']} jobs")
for job in jobs_data['jobs']:
    print(f"- {job['job_title']} at {job['company_name']}")
```

## Docker Commands

```bash
# Build image
docker-compose build

# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down

# Rebuild and restart
docker-compose down && docker-compose up --build -d
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LINKEDIN_EMAIL` | LinkedIn email/username | Yes* |
| `LINKEDIN_PASSWORD` | LinkedIn password | Yes* |
| `LINKEDIN_LI_AT` | LinkedIn li_at cookie | Yes* |
| `PORT` | API server port | No (default: 8000) |
| `HOST` | API server host | No (default: 0.0.0.0) |
| `DEBUG_MODE` | Enable debug logging | No |

*Either email/password OR session cookies are required.

## Rate Limiting & Best Practices

- The scraper includes built-in delays between requests
- Uses rotating user agents to avoid detection
- Respects LinkedIn's rate limits with exponential backoff
- Avoid running too frequently to prevent account restrictions

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check your credentials in `.env`
2. **CAPTCHA Required**: Use session cookies instead of username/password
3. **No Jobs Found**: Verify your search URLs are correct
4. **Rate Limited**: Increase delays in `config.json`

### Logs

Check container logs for detailed information:
```bash
docker-compose logs -f linkedin-scraper-api
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## License

This project is licensed under the terms specified in the LICENSE file.
