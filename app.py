#!/usr/bin/env python3
"""
LinkedIn Job Scraper API Server

This FastAPI server provides endpoints to scrape LinkedIn job listings
and return them as JSON instead of CSV files.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import logging
import sys
from datetime import datetime
import uvicorn

# Import the scraper components
from scraper_final import (
    linkedin_auth, Config, load_config_from_json,
    fetch_job_ids_from_url, fetch_job_details,
    add_random_headers, log_separator, logger
)

# Initialize FastAPI app
app = FastAPI(
    title="LinkedIn Job Scraper API",
    description="API server for scraping LinkedIn job listings",
    version="1.0.0"
)

# Global variable to store job results
job_cache = {}

class JobRequest(BaseModel):
    search_urls: Optional[List[Dict[str, str]]] = None
    max_pages: Optional[int] = 1
    filter_easy_apply: Optional[bool] = False

class JobResponse(BaseModel):
    success: bool
    message: str
    jobs: List[Dict[str, Any]]
    total_jobs: int
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting LinkedIn Job Scraper API...")
    
    # Load configuration
    try:
        load_config_from_json("config.json")
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Authenticate with LinkedIn
    logger.info("Authenticating with LinkedIn...")
    if not linkedin_auth.login():
        logger.error("Failed to authenticate with LinkedIn")
        sys.exit(1)
    
    # Initialize headers
    add_random_headers(Config.INITIAL_HEADERS_COUNT)
    logger.info("API server started successfully")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LinkedIn Job Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/jobs": "GET - Scrape jobs using default configuration",
            "/jobs/custom": "POST - Scrape jobs with custom parameters",
            "/health": "GET - Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "authenticated": linkedin_auth.is_authenticated,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/jobs", response_model=JobResponse)
async def scrape_jobs_default():
    """
    Scrape jobs using the default configuration from config.json
    """
    try:
        log_separator("API Job Scraping Request - Default Configuration")
        
        all_job_data = []
        unique_jobs = set()
        
        logger.info(f"Processing {len(Config.SEARCH_URLS)} search URLs from config")
        
        for search_config in Config.SEARCH_URLS:
            logger.info(f"Processing search: {search_config['name']}")
            
            job_info_list = fetch_job_ids_from_url(search_config)
            
            for job_info in job_info_list:
                job_id = job_info['job_id']
                if job_id in unique_jobs:
                    continue
                    
                job_detail = fetch_job_details(job_info)
                if job_detail:
                    all_job_data.append(job_detail)
                    unique_jobs.add(job_id)
        
        response = JobResponse(
            success=True,
            message=f"Successfully scraped {len(all_job_data)} jobs",
            jobs=all_job_data,
            total_jobs=len(all_job_data),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"API request completed: {len(all_job_data)} jobs scraped")
        return response
        
    except Exception as e:
        logger.error(f"Error during job scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/jobs/custom", response_model=JobResponse)
async def scrape_jobs_custom(request: JobRequest):
    """
    Scrape jobs with custom parameters
    """
    try:
        log_separator("API Job Scraping Request - Custom Configuration")
        
        # Use custom parameters or fallback to config defaults
        search_urls = request.search_urls or Config.SEARCH_URLS
        max_pages = request.max_pages or Config.MAX_PAGES_PER_SEARCH
        
        # Temporarily update config for this request
        original_max_pages = Config.MAX_PAGES_PER_SEARCH
        Config.MAX_PAGES_PER_SEARCH = max_pages
        
        all_job_data = []
        unique_jobs = set()
        
        logger.info(f"Processing {len(search_urls)} custom search URLs")
        
        for search_config in search_urls:
            logger.info(f"Processing search: {search_config.get('name', 'Custom Search')}")
            
            job_info_list = fetch_job_ids_from_url(search_config)
            
            for job_info in job_info_list:
                job_id = job_info['job_id']
                if job_id in unique_jobs:
                    continue
                    
                job_detail = fetch_job_details(job_info)
                if job_detail:
                    # Apply Easy Apply filter if requested
                    if request.filter_easy_apply and not job_detail.get('has_easy_apply', False):
                        continue
                    all_job_data.append(job_detail)
                    unique_jobs.add(job_id)
        
        # Restore original config
        Config.MAX_PAGES_PER_SEARCH = original_max_pages
        
        response = JobResponse(
            success=True,
            message=f"Successfully scraped {len(all_job_data)} jobs with custom parameters",
            jobs=all_job_data,
            total_jobs=len(all_job_data),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Custom API request completed: {len(all_job_data)} jobs scraped")
        return response
        
    except Exception as e:
        logger.error(f"Error during custom job scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Custom scraping failed: {str(e)}")

@app.get("/jobs/search")
async def search_jobs(
    keywords: str = Query(..., description="Job search keywords"),
    location: str = Query("101282230", description="LinkedIn location ID"),
    experience_level: str = Query("2", description="Experience level (1=Internship, 2=Entry level, 3=Associate, 4=Mid-Senior level, 5=Director, 6=Executive)"),
    time_filter: str = Query("r3600", description="Time filter (r86400=24h, r3600=1h, r604800=1w)"),
    max_pages: int = Query(1, description="Maximum pages to scrape")
):
    """
    Search jobs with specific parameters
    """
    try:
        # Construct LinkedIn search URL
        search_url = f"https://www.linkedin.com/jobs/search/?f_E={experience_level}&f_TPR={time_filter}&geoId={location}&keywords={keywords}&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"
        
        search_config = {
            "name": f"{keywords} Jobs - Custom Search",
            "url": search_url,
            "description": f"Custom search for {keywords} jobs"
        }
        
        # Create custom request
        custom_request = JobRequest(
            search_urls=[search_config],
            max_pages=max_pages,
            filter_easy_apply=False
        )
        
        return await scrape_jobs_custom(custom_request)
        
    except Exception as e:
        logger.error(f"Error during job search: {e}")
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")

if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port) 