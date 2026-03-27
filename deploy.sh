#!/bin/bash

# --- Oracle Cloud Deployment Script ---
# This script installs Docker and starts the Stock Market project.

set -e

echo "🚀 Starting Oracle Cloud Deployment..."

# 1. Update and Install Dependencies
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common git

# 2. Install Docker (if not installed)
if ! command -v docker &> /dev/null
then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
else
    echo "✅ Docker already installed."
fi

# 3. Install Docker Compose
if ! command -v docker-compose &> /dev/null
then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed."
fi

# 4. Preparing Project
# (Assuming project is already cloned or will be cloned manually)
# Note: If you haven't cloned the repo, do it now: git clone <your-repo-url>
# cd <repo-name>

# 5. Build and Start
echo "🏗️ Building and starting containers..."
docker-compose -f docker-compose.prod.yml down || true
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 6. Database Migrations
echo "🗄️ Running migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --no-input
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --no-input

echo "✨ Deployment Complete! Your site should be live at your Public IP."
echo "🔗 Visit: http://<YOUR_ORACLE_IP>"
