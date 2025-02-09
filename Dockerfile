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
      py3-pandas

# Set the working directory to /home/node/.n8n
WORKDIR /home/node/

# Copy your Python script and config file into the working directory
COPY scraper_final.py config.json ./

# Change ownership of the copied files so that the 'node' user can access them
RUN chown node:node config.json scraper_final.py && \
    chmod 644 config.json

# Switch back to the default non-root user (typically 'node')
USER node
EXPOSE 5678