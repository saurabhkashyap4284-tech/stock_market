#!/bin/bash

# --- AWS EC2 Deployment Script ---
# This script configures a SWAP file for the 1GB RAM limit and starts the project.

set -e

echo "🚀 Starting AWS EC2 Deployment (Free Tier)..."

# 1. Create SWAP File (CRITICAL for 1GB RAM)
if [ ! -f /swapfile ]; then
    echo "💾 Creating 2GB Swap file for extra Virtual RAM..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "✅ Swap file created and activated."
else
    echo "✅ Swap file already exists."
fi

# 2. Update and Install Dependencies
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common git

# 3. Install Docker (if not installed)
if ! command -v docker &> /dev/null
then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
else
    echo "✅ Docker already installed."
fi

# 4. Install Docker Compose
if ! command -v docker-compose &> /dev/null
then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed."
fi

# 5. Build and Start
echo "🏗️ Building and starting containers..."
# Using the same production configuration prepared for OCI
docker-compose -f docker-compose.prod.yml down || true
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 6. Database Migrations
echo "🗄️ Running migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --no-input
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --no-input

echo "✨ AWS Deployment Complete!"
echo "🔗 Visit: http://<YOUR_AWS_PUBLIC_IP>"
