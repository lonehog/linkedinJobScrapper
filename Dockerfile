# Use the official n8n image from Docker Hub (Debian-based)
FROM n8nio/n8n:latest

# Switch to root to install additional packages
USER root

# Update package index, install Python3 and pip, then install Python libraries
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
 && pip3 install --no-cache-dir \
    requests \
    beautifulsoup4 \
    pandas \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory (you can adjust if needed)
WORKDIR /home/node/

# Copy your Python script and config file
COPY scraper_final.py config.json ./

# Change ownership so the 'node' user can access them
RUN chown node:node config.json scraper_final.py && \
    chmod 644 config.json

# Switch back to the default non-root user
USER node

# Set environment variables for n8n
ENV N8N_PORT=5678 \
    PORT=5678 \
    N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS="true" \
    N8N_LISTEN_ADDRESS="0.0.0.0" \
    N8N_PROTOCOL="https" \
    N8N_HOST="n8n.cedric-coding-projects.com" \
    WEBHOOK_TUNNEL_URL="https://n8n.cedric-coding-projects.com/" \
    WEBHOOK_URL="https://n8n.cedric-coding-projects.com/" \
    N8N_SECURE_COOKIE="true"

# Expose n8n’s default port
EXPOSE 5678