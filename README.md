# 🌟 LinkedIn Job Scraper with Python and Deploying with n8n

## 📑 Table of Contents
- [⚠️ Disclaimer](#-disclaimer)
- [📘 Introduction](#-introduction)
- [📋 Prerequisites](#-prerequisites)
- [🚀 Quick Start Guide](#-quick-start-guide)
  - [1️⃣ Prepare Your Files](#1️⃣-prepare-your-files)
  - [2️⃣ Build the Docker Image](#2️⃣-build-the-docker-image)
  - [3️⃣ Run the Docker Container](#3️⃣-run-the-docker-container)
  - [4️⃣ Access n8n and Import Your Workflow](#4️⃣-access-n8n-and-import-your-workflow)
  - [5️⃣ View the Results](#5️⃣-view-the-results)
- [🔍 Overview](#-overview)
- [🏗️ Project Structure](#-project-structure)
- [⚙️ Configuration](#-configuration)
- [📂 Files Included](#-files-included)
- [🛠️ Step-by-Step Instructions](#️-step-by-step-instructions)
  - [1️⃣ Review and Update Files](#1️⃣-review-and-update-files)
  - [2️⃣ Build the Docker Image](#2️⃣-build-the-docker-image)
  - [3️⃣ Run the Docker Container](#3️⃣-run-the-docker-container)
  - [4️⃣ Access n8n and Import Your Workflow](#4️⃣-access-n8n-and-import-your-workflow)
  - [5️⃣ Running and Testing the Automation](#5️⃣-running-and-testing-the-automation)
  - [6️⃣ Maintenance and Updates](#6️⃣-maintenance-and-updates)
- [💡 Tips for Beginners](#-tips-for-beginners)
- [☁️ Deploying on a Cloud Server](#️-deploying-on-a-cloud-server)
  - [🚀 Using Render](#-using-render)
  - [📜 Step-by-Step Deployment on Render](#-step-by-step-deployment-on-render)
  - [☁️ Other Cloud Options](#-other-cloud-options)
- [🎯 Recommendation](#-recommendation)
- [🎯 Conclusion](#-conclusion)
- [📜 License](#license)

---

## ⚠️ Disclaimer

This project is intended for educational purposes only. The use of web scraping to collect data from LinkedIn or any other website may violate the terms of service of those websites. Please ensure that you have the necessary permissions and comply with all applicable laws and regulations before using this scraper. The authors of this project are not responsible for any misuse or legal consequences resulting from the use of this tool.

---

## 📘 Introduction

This project combines a custom Python scraper with the powerful automation tool [n8n](https://n8n.io/) and Docker to collect job listings from LinkedIn based on specified search queries. The scraped data is then processed and pushed to Notion (or any other destination you choose) via an automated workflow.

This guide will walk you through setting up your **LinkedIn Job Scraper** using Docker and n8n. If you’re new to Docker and automation, follow these step-by-step instructions carefully.


---
## 📋 Prerequisites

Before you begin, make sure you have the following installed on your computer:

- **Docker:**  
   - **What is Docker?** Docker is a platform that allows you to run applications in isolated containers.
   - **How to Install Docker:**
     - **For Windows/Mac:**  
       Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop). Follow the installation prompts.
     - **For Linux:**  
       Follow the installation instructions specific to your distribution, such as using the [Docker Engine installation guide](https://docs.docker.com/engine/install/).
   - **Verify Installation:**  
     Open a terminal (or Command Prompt) and run:
     ```sh
     docker --version
     ```
     You should see output that includes the Docker version number.

---

## 🚀 Quick Start Guide

This guide provides two approaches to get your **LinkedIn Job Scraper** running: one using Docker and one running directly on your local machine.

---

### Without Using Docker

#### 1️⃣ Prepare Your Files

Ensure you have the following files in your working folder:
- `config.json`
- `scraper_final.py`
- `my_n8n_template.json`
-  `requirements.txt`

*Tip:* Missing files can be retrieved from your project repository or your project maintainer.

---

#### 2️⃣ Set Up Your Environment

1. Install Python 3 from [python.org](https://www.python.org/) if it isn’t already installed.
2. Install the required Python libraries. If a requirements file is available, run:
  ```sh
  pip install -r requirements.txt
  ```
  Otherwise, install dependencies manually (such as `requests`, `BeautifulSoup`, and `pandas`).

---

#### 3️⃣ Run the Python Script

Run the scraper manually:
```sh
python scraper_final.py
```
> ### ❗IMPORTANT ❗
> 
> ### **This alone is sufficient to list the jobs, as it will collect and save all job listings into the “`jobs_listing.csv`” file directly. The rest can be skipped**

---

#### 4️⃣ Start n8n Manually

1. Install n8n following the [n8n documentation](https://docs.n8n.io/).
2. Launch n8n by running:
  ```sh
  n8n
  ```
3. Open your browser and navigate to:
  ```
  http://localhost:5678
  ```
4. In the n8n interface, import the `my_n8n_template.json` file:
  - Click on **Import** in the workflow menu.
  - Upload or paste the JSON content.
  - Execute the workflow.

---

### Using Docker

#### 1️⃣ Prepare Your Files

Ensure that you have the following files in the same folder:
- `Dockerfile`
- `config.json`
- `scraper_final.py`
- `my_n8n_template.json`

*Tip:* If any of these files are missing, check your project repository or ask your project maintainer.

---

#### 2️⃣ Build the Docker Image

1. Open your terminal.
2. Navigate to the folder containing your files.
3. Run:
  ```sh
  docker build -t linkedin-scraper .
  ```
  *Note:* This builds an image named `linkedin-scraper` based on your Dockerfile. For more details, see the [Docker Build Documentation](https://docs.docker.com/engine/reference/commandline/build/).

---

#### 3️⃣ Run the Docker Container

Start your container with:
```sh
docker run -d -p 5678:5678 --name linkedin-scraper-container linkedin-scraper
```
- `-d` runs it in detached mode.
- `-p 5678:5678` maps the container’s port.
- `--name` assigns a name to your container.

For additional options, visit the [Docker Run Command Guide](https://docs.docker.com/engine/reference/commandline/run/).

---

#### 4️⃣ Access n8n and Import Your Workflow

1. Open your browser and go to:
  ```
  http://localhost:5678
  ```
2. In the n8n interface, import the `my_n8n_template.json` file:
  - Click the **Import** option from the workflow menu.
  - Upload or paste the JSON content.
  - Run the workflow.

If you’re new to n8n, check out the [n8n Import Guide](https://docs.n8n.io/).

---

#### 5️⃣ View the Results

After running the workflow, locate the `job_listing.csv` file in your project folder. This file should contain the scraped LinkedIn job listings.

🎉 **Congratulations**—you’ve successfully set up your LinkedIn Job Scraper using Docker!

---

#### 5️⃣ View the Results

After running the workflow, check your project folder for the generated `job_listing.csv` file containing the LinkedIn job listings scraped by your script.

🎉 **Congratulations**—you’ve successfully set up your LinkedIn Job Scraper without using Docker!

👉 For troubleshooting and advanced configurations, refer to the documentation and guides provided.


---
## 🔍 Overview

The **LinkedIn Job Scraper** project is an end-to-end solution for scraping job listings from LinkedIn. It leverages:

- **Python** for web scraping (with `requests`, `BeautifulSoup`, and `pandas`).
- **n8n** for visual automation workflows that run the scraper, process CSV data, and (optionally) integrate with Notion.
- **Docker** to containerize the environment so that you can run the entire system in a consistent, isolated environment.
- **Cloud deployment** options (with Render, Heroku, AWS, etc.) to run the automation continuously.

The project extracts key job details such as job ID, company name, title, posting time, location, description, and more. It uses random user agents and robust error handling to work around LinkedIn’s request limits.

---

## 🏗️ Project Structure

Your project folder should include the following key files:

- **`Dockerfile`**  
  Creates a Docker image based on the official n8n image, installs Python3, pip, and necessary libraries, and copies the scraper files.

- **`config.json`**  
  A JSON configuration file that defines:
  - The base URLs used for scraping.
  - Search queries (keywords, location, etc.).
  - Timeout, delay, retry settings.
  - CSV filename and output fields.

- **`scraper_final.py`**  
  The Python script that performs the actual scraping:
  - Loads configuration.
  - Generates random headers.
  - Scrapes job IDs and job details.
  - Saves the scraped data into a CSV file.
  - Provides detailed logging (with colored output) to help with debugging.

- **`my_n8n_template.json`**  
  An n8n workflow template that:
  - Triggers the Python scraper.
  - Loads the generated CSV.
  - Parses and transforms the data.
  - Pushes job entries into a Notion database.
  - Handles duplicate entries and error logging.

---

## ⚙️ Configuration

1. **`config.json`**  
   Customize the configuration parameters such as:
   - `BASE_LIST_URL` and `BASE_JOB_URL`: Base URLs for job listings and job details.
   - `SEARCH_QUERIES`: An array of search queries with keywords, location, and filters.
   - `NUM_JOBS_PER_QUERY`: Number of job IDs to fetch per query.
   - Timeout, delays, retry settings, and output CSV filename.
   
2. **n8n Workflow (`my_n8n_template.json`)**
  This JSON file defines the n8n workflow:
    - Nodes include:
    - Execute Command Node: Runs the Python scraper.
    - File Nodes: Load the generated CSV and configuration file.
    - Data Transformation Nodes: Parse CSV data, remove duplicates, and transform job data.
    - Notion Nodes (Optional): Create or update job entries in a Notion database.
    - You can copy and paste the content of `my_n8n_template.json` into a workflow inside n8n


---

## 📂 Files Included  

- **Dockerfile** – Builds a Docker image for n8n with all the necessary Python dependencies.
- **config.json** – Contains your scraper configuration (LinkedIn URLs, search queries, CSV filename, etc.).
- **scraper_final.py** – The Python script that performs the actual scraping.
- **my_n8n_template.json** – An n8n workflow that orchestrates the scraper process and data handling.

---

## 🛠️ Step-by-Step Instructions  

### 1️⃣ Review and Update Files  

#### Dockerfile  
- Starts with the official n8n image.
- Installs Python3, pip, and libraries (`requests`, `BeautifulSoup`, `pandas`).
- Sets the working directory to `/home/node/` and copies `scraper_final.py` and `config.json`.
- Adjusts file permissions so the `node` user can access the files.
- Exposes port `5678`.

For a primer on Dockerfiles, see the [Dockerfile Basics](https://docs.docker.com/engine/reference/builder/).

#### config.json  
- Verify that your configuration values (base URLs, search queries, timeouts, etc.) match your needs.
- Adjust `"NUM_JOBS_PER_QUERY"` or add more queries as needed.

#### scraper_final.py  
- Contains your web scraping logic.
- Reads from `config.json` to fetch job listings.
- Ensure any changes in configuration are properly reflected here.  
  Learn more about handling JSON in Python at the [Python JSON documentation](https://docs.python.org/3/library/json.html).

#### my_n8n_template.json  
- Defines your n8n workflow, including nodes for:
  - Running the scraper script.
  - Loading and processing CSV data.
  - Interacting with Notion.
- Import this file into n8n to view and modify the workflow.  
  For more on n8n workflows, visit the [n8n Workflows Documentation](https://docs.n8n.io/).

---

### 2️⃣ Build the Docker Image  

Run the following command:

```sh
docker build -t linkedin-scraper .
```
For additional details, refer to the [Docker Build Guide](https://docs.docker.com/engine/reference/commandline/build/).

---

### 3️⃣ Run the Docker Container  

Launch your container with:

```sh
docker run -d -p 5678:5678 --name linkedin-scraper-container linkedin-scraper
```
Check out the [Docker Run Command Documentation](https://docs.docker.com/engine/reference/commandline/run/) for more info.

---

### 4️⃣ Access n8n and Import Your Workflow  

Open your browser and navigate to:

```
http://localhost:5678
```
Import the `my_n8n_template.json` file into n8n and run the workflow.  

For help with importing workflows, see the [n8n Import Guide](https://docs.n8n.io/).

---

### 5️⃣ Running and Testing the Automation  

- Trigger the workflow manually or set up a schedule trigger.
- Check the n8n logs (via the editor or using Docker logs) to troubleshoot any issues.
- Verify that the `job_listing.csv` file is generated with the correct data.  
  Learn more about viewing logs with [n8n Execution Logs](https://docs.n8n.io/).

---

### 6️⃣ Maintenance and Updates  

- Update your files as needed and rebuild the Docker image.
- Regularly check your logs to ensure smooth operation.  
  For more on Docker logging, see the [Docker Logging Documentation](https://docs.docker.com/config/containers/logging/).

### 💡 Tips for Beginners
- Security Settings:
  The default settings work well for learning. Once you’re more comfortable, consider exploring enhanced security practices.

- Experiment with n8n:
  Use n8n’s visual workflow editor to adjust parameters and understand node functionality.

- Use Online Resources:
  Helpful resources include:

  - [Docker Documentation](https://docs.docker.com/)
  - [n8n Documentation](https://docs.n8n.io/)
  - [Python Web Scraping Tutorials](https://www.geeksforgeeks.org/python-web-scraping-tutorial/)
Backup Your Files:
Always back up your config.json and workflow files before making changes.


---

# ☁️ Deploying on a Cloud Server

If you want your scraper to run 24/7 in the cloud, here's how to deploy it using **Render**—an excellent choice for beginners:

---

## 🚀 Using Render  

### What Render Offers:  

- **Always-on Services**: Render is designed for continuous operation, so your scraper will run 24/7 without manual intervention.  
- **Managed Infrastructure**: You don’t need to worry about server updates, security patches, or scaling. Render handles all that for you.  
- **Simple Deployment**: You can deploy your Docker container directly from your repository or by uploading your Dockerfile.  

---

## 📜 Step-by-Step Deployment on Render  

### 1️⃣ Sign Up and Log In  
- Go to [Render.com](https://render.com/) and create an account (free tier available).  

### 2️⃣ Create a New Web Service  
- In the Render dashboard, click on **“New”** and then select **“Web Service”**.  
- Connect your Git repository if your project is hosted on **GitHub, GitLab, or Bitbucket**, or upload your files manually.  

### 3️⃣ Configure Your Service  
- **Set the Environment** to **Docker**.  
- In the **Build Command** field, use:  

```sh
docker build -t linkedin-scraper .
```
- In the **Start Command**, ensure your container starts the n8n process (this is already handled by the base image).  

### 4️⃣ Set Environment Variables (Optional)  
- If your configuration requires environment variables, set them in the **Environment** section.  

### 5️⃣ Deploy  
- Click **“Create Web Service”**.  
- Render will build and deploy your Docker container.  
- Once deployed, Render will provide you with a **URL** where your service is running.  

### 6️⃣ Monitor Your Service  
- Use Render’s **dashboard** to check logs, monitor uptime, and view performance metrics.  

For more detailed instructions, visit [Deploying on Render](https://render.com/docs).  

---

## ☁️ Other Cloud Options  

|  | Cloud Provider       | Ease of n8n Setup / Beginner Friendliness                                                                                                                     | Continuous Operation (24/7)                                 | Compute Option / Hardware Specs                                                  | Free Tier Benefits                                                                                                        | Duration                              | Pros                                                                                      | Cons                                                                                          | Price Insight                                                                                                         | Pricing / Free Tier Links                                                                                                                                                                                                                                  |
|------|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|---------------------------------------|-------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1    | **Render**           | **Extremely beginner‑friendly.** Render offers a fully managed environment where you deploy your Docker container with one‑click setups. Minimal server administration is required. | Designed to run continuously; Render’s free web services remain always on provided usage limits aren’t exceeded. | Starter containers typically run on shared CPU (roughly 0.2–0.5 vCPU), ~512 MB RAM, with ephemeral disk storage. | Always Free for static sites and small web services with free usage limits (e.g. 750 hours/month)                         | **Always Free**                       | Very simple deployment; no manual security or OS updates; managed scaling and updates.   | Limited resource allocation—if your automation grows, you may need to upgrade.                | Paid plans start around **$7–$8/month** for more resources.                                                           | [Render Free Tier & Pricing](https://render.com/pricing)                                                                                                                                                                                                   |
| 2    | **Heroku**           | **Extremely easy for beginners.** Heroku abstracts server management completely; you deploy via Git. (For true 24/7 uptime, consider upgrading to Hobby dynos.)        | Free dynos sleep after 30 minutes of inactivity; to run 24/7, you must upgrade to a Hobby dyno.                        | Free dynos offer roughly 512 MB RAM and shared CPU resources; Hobby dynos offer similar specs but remain always on.        | Free dynos for lightweight NodeJS apps; integrated Git deployment; numerous add‑ons available                           | **Always Free (with sleep)** (24/7 if upgraded) | Very simple to deploy; excellent documentation and community support; managed environment.  | Dynos “sleep” on the free plan, which may interrupt continuous trigger listening.             | Hobby dynos (always on) cost about **$7/month per dyno**.                                                               | [Heroku Free Tier](https://www.heroku.com/free) / [Heroku Pricing](https://www.heroku.com/pricing)                                                                                                                                                        |
| 3    | **IBM Cloud**        | **Moderately beginner‑friendly.** IBM Cloud provides Lite plans with guided wizards for deploying containers and functions without deep server management.         | Lite plans are designed to run continuously, though service quotas and inactivity policies may apply.                   | Managed container options typically offer 256–512 MB RAM on shared hardware; specifics vary by service.                   | Over 40 always‑free products (Cloud Functions, databases like Db2/Cloudant, etc.) plus a $200 trial credit for additional usage | **Always Free for Lite Plans**        | Wide range of managed services; minimal configuration required; menu‑driven, beginner‑oriented. | Some quotas are limited and may suspend if inactive; less consistent performance across services.  | Additional resources start at roughly **$10/month** when you scale beyond Lite limits.                                  | [IBM Cloud Free Tier](https://www.ibm.com/cloud/free) / [IBM Pricing](https://www.ibm.com/cloud/pricing)                                                                                                                                                   |
| 4    | **Oracle Cloud**     | **Good for learners willing to manage a basic server.** Oracle provides persistent Linux VMs that require some initial configuration (security, SQL, etc.).      | The persistent VMs run 24/7 continuously—ideal for listening to triggers—if configured correctly.                       | Two Always Free VMs: each typically with 1 OCPU (roughly 1 vCPU equivalent or 0.5–1 shared vCPU) and 1 GB RAM; persistent block storage available. | Always Free: Persistent compute VMs, free block storage, free databases, load balancer, etc.                                | **Always Free (indefinite)**          | Persistent environment; plenty of free add‑on services; full control over your server environment.   | Requires manual setup for security, database configuration, and maintenance; more technical.     | Upgrading to larger instances usually starts around **$5–$10/month** (pay‑as‑you‑go for extra resources).                  | [Oracle Cloud Free Tier & Pricing](https://www.oracle.com/cloud/free/)                                                                                                                                                                                   |
| 5    | **AWS**              | **Powerful but with a steeper learning curve.** AWS offers both serverless (Lambda) and full VMs (EC2). For a persistent n8n setup, EC2 requires manual configuration. | Lambda functions run continuously when triggered, but for always‑on, an EC2 instance is required—which is free for 12 months. | EC2 micro instance: typically 1 vCPU (burstable) and 1 GB RAM; Lambda is event‑driven with no persistent hardware.         | Lambda: 1M free requests/month (always free); EC2: 750 free hours/month for 12 months plus free DynamoDB, SNS, etc.           | **EC2: 12 months free; Lambda: Always Free** | Extremely robust; wide range of services; excellent documentation and scalability.              | EC2 free tier expires after 12 months; overall service complexity and manual configuration can be overwhelming.  | On‑demand EC2 micro instances cost roughly **$8–$10/month**; Lambda overages billed at about **$0.20 per million** extra invocations. | [AWS Free Tier](https://aws.amazon.com/free/) / [AWS Pricing](https://aws.amazon.com/pricing/)                                                                                                                                                           |
| 6    | **Google Cloud Platform (GCP)** | **Moderate learning curve.** GCP offers a free F1‑micro instance in select regions and managed services like Cloud Functions. Setup requires some configuration.  | The F1‑micro instance is designed for continuous operation in supported regions, though usage caps apply.                   | F1‑micro: roughly 0.2 vCPU (burstable) and 0.6 GB memory; persistent disk up to 30 GB HDD is available in free tier.       | Always Free: 1 F1‑micro instance (30 GB HDD, 1 GB outbound) in select regions; free Cloud Function invocations                  | **F1‑micro: Always Free (select regions)** | Good integration of managed services; reliable for small-scale continuous workloads.            | Free instance availability is limited by region; setup and security configuration may be challenging for beginners. | F1‑micro instances typically cost around **$5–$7/month** if not free; additional services billed per use.                  | [GCP Free Tier](https://cloud.google.com/free)                                                                                                                                                                                                           |
| 7    | **Microsoft Azure**  | **Least beginner‑friendly.** Azure provides managed VMs and functions but requires more cloud management expertise. For n8n, you'll need to manually configure your B1S VM.     | VMs run continuously once set up, but the free tier only lasts for 12 months; after that, it requires payment for continuous operation. | B1S VM: typically 1 vCPU and 1 GB RAM, with 30 GB SSD storage; additional managed services available.                    | 12‑month free tier for VMs plus some always‑free services on a limited basis                                                       | **12 months free for VMs**             | Extensive service portfolio; deep integration with Microsoft tools; very robust and secure.       | Free tier expires after 12 months; steeper learning curve; configuration is more complex and geared toward enterprise.   | B1S VMs typically cost around **$4–$8/month** on pay‑as‑you‑go after the free period expires.                               | [Azure Free Tier](https://azure.microsoft.com/en-us/free/) / [Azure Pricing](https://azure.microsoft.com/en-us/pricing/)                                                                   |


# In Practice: What This Means for Your n8n Automation

### **Render**
  - **Setup:** Upload your n8n Docker container via a simple dashboard.
  - **Continuous Operation:** The service is designed to run 24/7 without manual intervention.
  - **Hardware:** You get shared CPU and moderate memory (around 512 MB), which is ideal for light to moderate automation loads.
  - **Plain Terms:** You basically “drop” your app in and Render handles everything—no need to worry about security patches, OS updates, or uptime.

### **Heroku**
  - **Setup:** Deploy your code with Git; Heroku manages the environment.
  - **Continuous Operation:** Free dynos sleep after 30 minutes of inactivity. For always‑on, upgrade to Hobby dynos (costing around $7/month).
  - **Hardware:** Free dynos provide roughly 512 MB RAM on shared hardware.
  - **Plain Terms:** It’s super easy to get started, but if you need your automation to be always running, you might have to spend a little on a Hobby plan.

### **IBM Cloud**
  - **Setup:** Use guided wizards for deploying containers or functions with minimal manual configuration.
  - **Continuous Operation:** Lite plans are designed to be persistent, although some services might suspend after long inactivity.
  - **Hardware:** Typically provides modest shared resources (256–512 MB RAM).
  - **Plain Terms:** IBM Cloud offers a range of managed, free services that are good for experimentation, without requiring you to manage a full server.

### **Oracle Cloud**
  - **Setup:** You set up your own Linux VMs. This gives you full control but requires learning basic server management (security updates, DB configuration, etc.).
  - **Continuous Operation:** VMs run 24/7 continuously.
  - **Hardware:** Each VM comes with about 1 vCPU (shared) and 1 GB RAM.
  - **Plain Terms:** You get your own mini‑server that always runs—but you’ll need to learn a bit about setting it up and keeping it secure.

### **AWS**
  - **Setup:** You can choose a serverless approach with Lambda (which is easier for small tasks) or deploy an EC2 instance for persistent operation (which requires more setup).
  - **Continuous Operation:** Lambda is always free for event‑driven tasks; EC2 free tier lasts 12 months.
  - **Hardware:** An EC2 micro instance typically offers 1 vCPU and 1 GB RAM.
  - **Plain Terms:** AWS is very powerful but can be overwhelming due to its many services and configuration steps.

### **GCP**
  - **Setup:** Deploy on a free F1‑micro instance in supported regions; configuration for security and networking is required.
  - **Continuous Operation:** The F1‑micro runs 24/7 in regions where it’s available free.
  - **Hardware:** Offers about 0.2 vCPU (burstable) and around 0.6 GB memory, with 30 GB HDD storage.
  - **Plain Terms:** GCP provides a free mini‑server in certain regions but may require a bit more reading to set up properly.

### **Microsoft Azure**
  - **Setup:** Deploying on Azure requires manual configuration of a B1S VM, along with setting up security and storage.
  - **Continuous Operation:** VMs run continuously once set up, but the free tier is only available for 12 months.
  - **Hardware:** Typically 1 vCPU and 1 GB RAM with 30 GB SSD storage.
  - **Plain Terms:** Azure is robust and secure but is more complex and better suited for enterprise use rather than a simple hobby project.

### **Summary for Beginners Needing Continuous 24/7 Operation**
  - **Best Overall for Ease & Continuity:** Render tops the list because it offers a fully managed, always‑on environment with a simple, beginner‑friendly deployment process.
  - **Next Best:** Heroku is very easy to set up, though its free tier “sleeps” — an upgrade to Hobby dynos is recommended for continuous operation.
  - **For More Control:** IBM Cloud and Oracle Cloud offer persistent services with more free features, but require a bit more initial setup.
  - **More Complex Options:** AWS, GCP, and Azure are powerful but have steeper learning curves and may not be ideal if you want minimal setup hassle.

Enjoy building and automating!

---

## 🎯 Recommendation  

For beginners looking for an **always-on, hassle-free deployment**, **Render** is the best choice.  
If you need **more control**, AWS EC2 or Heroku may be better options depending on your experience level.  


---

## 🎯 Conclusion  

You have now set up your **LinkedIn Job Scraper** using **n8n and Docker**.  
For a cloud deployment, **Render** is a great choice for beginners, while **AWS EC2** and **Heroku** provide more control.

If you run into issues, consult the following resources:

- [Docker Troubleshooting](https://docs.docker.com/config/containers/troubleshoot/)
- [n8n Documentation](https://docs.n8n.io/)
- [Render Documentation](https://render.com/docs)

Happy scraping! 🚀

## License

This project is licensed under the [MIT License](LICENSE).
