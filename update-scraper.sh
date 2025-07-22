#!/bin/bash

# LinkedIn Scraper - Auto Update Script
# This script pulls the latest Docker image and restarts the service

set -e  # Exit on any error

# Configuration
GITHUB_USERNAME="YOUR_USERNAME"  # Replace with your GitHub username
IMAGE_NAME="ghcr.io/${GITHUB_USERNAME}/n8n_linkedinjobscrapper:latest"
COMPOSE_FILE="docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 LinkedIn Scraper Update Script${NC}"
echo "=================================="

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Production compose file not found: $COMPOSE_FILE${NC}"
    echo -e "${YELLOW}💡 Make sure you're in the project directory with the compose file${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}💡 Create a .env file with your LinkedIn credentials${NC}"
    exit 1
fi

echo -e "${BLUE}🎯 Target image: ${IMAGE_NAME}${NC}"
echo ""

# Pull the latest image
echo -e "${YELLOW}📥 Pulling latest image...${NC}"
if docker pull "$IMAGE_NAME"; then
    echo -e "${GREEN}✅ Successfully pulled latest image${NC}"
else
    echo -e "${RED}❌ Failed to pull image${NC}"
    echo -e "${YELLOW}💡 Make sure the image exists and you have access${NC}"
    exit 1
fi

# Stop current containers
echo -e "${YELLOW}🛑 Stopping current containers...${NC}"
if docker-compose -f "$COMPOSE_FILE" down; then
    echo -e "${GREEN}✅ Containers stopped${NC}"
else
    echo -e "${YELLOW}⚠️  No running containers found or failed to stop${NC}"
fi

# Start with new image
echo -e "${YELLOW}🚀 Starting with latest image...${NC}"
if docker-compose -f "$COMPOSE_FILE" up -d; then
    echo -e "${GREEN}✅ Service started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start service${NC}"
    exit 1
fi

# Wait a bit and check health
sleep 10
echo -e "${YELLOW}🏥 Checking service health...${NC}"

# Check if container is running
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Container is running${NC}"
    
    # Try to check the health endpoint
    if command -v curl &> /dev/null; then
        if curl -f -s http://localhost:8000/health > /dev/null; then
            echo -e "${GREEN}✅ API health check passed${NC}"
        else
            echo -e "${YELLOW}⚠️  API health check failed - service may still be starting${NC}"
        fi
    else
        echo -e "${YELLOW}💡 Install curl to enable health checks${NC}"
    fi
else
    echo -e "${RED}❌ Container failed to start${NC}"
    echo -e "${YELLOW}📋 Check logs with: docker-compose -f $COMPOSE_FILE logs${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Update completed!${NC}"
echo -e "${BLUE}📡 API available at: http://localhost:8000${NC}"
echo -e "${BLUE}📖 API docs at: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}🔧 Useful commands:${NC}"
echo "  View logs:    docker-compose -f $COMPOSE_FILE logs -f"
echo "  Stop service: docker-compose -f $COMPOSE_FILE down"
echo "  Restart:      docker-compose -f $COMPOSE_FILE restart" 