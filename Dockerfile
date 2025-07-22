# Use the official n8n image from Docker Hub
FROM n8nio/n8n:latest

# Switch to root to install additional packages and Python dependencies
USER root

# Update Alpine package index and install Python3, pip, and the required Python libraries using apk
RUN apk update && \
    apk add --no-cache \
      python3 \
      py3-pip \
      py3-requests \
      py3-beautifulsoup4 \
      py3-pandas \
      py3-lxml

# Set the working directory to /home/node/.n8n
WORKDIR /home/node/

# Install additional Python packages not available through apk
RUN pip3 install python-dotenv

# Copy your Python script, config file, and requirements into the working directory
COPY scraper_final.py config.json requirements.txt ./

# Copy .env file if it exists (for local builds)
COPY .env* ./

# Install Python dependencies from requirements.txt
RUN pip3 install -r requirements.txt

# Change ownership of the copied files so that the 'node' user can access them
RUN chown node:node config.json scraper_final.py requirements.txt && \
    chmod 644 config.json scraper_final.py requirements.txt && \
    chown node:node .env* 2>/dev/null || true && \
    chmod 600 .env* 2>/dev/null || true

# Switch back to the default non-root user (typically 'node')
USER node
EXPOSE 5678