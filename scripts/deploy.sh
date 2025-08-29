#!/bin/bash

# Keelo.ai Deployment Script
# This script deploys the application to a production server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="keelo.ai"
SERVER_IP="${SERVER_IP:-}"
SSH_USER="${SSH_USER:-ubuntu}"
DEPLOY_PATH="/opt/keelo"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if server IP is provided
if [ -z "$SERVER_IP" ]; then
    print_error "SERVER_IP environment variable is not set"
    echo "Usage: SERVER_IP=xxx.xxx.xxx.xxx ./scripts/deploy.sh"
    exit 1
fi

print_status "Starting deployment to $DOMAIN ($SERVER_IP)"

# Step 1: Build Docker images locally
print_status "Building Docker images..."
docker-compose -f docker-compose.prod.yml build

# Step 2: Save Docker images
print_status "Saving Docker images..."
docker save -o keelo-frontend.tar ai-growth-agent-frontend:latest
docker save -o keelo-backend.tar ai-growth-agent-backend:latest

# Step 3: Copy files to server
print_status "Copying files to server..."
scp -r \
    docker-compose.prod.yml \
    .env.production \
    nginx/ \
    keelo-frontend.tar \
    keelo-backend.tar \
    $SSH_USER@$SERVER_IP:/tmp/

# Step 4: SSH to server and deploy
print_status "Deploying on server..."
ssh $SSH_USER@$SERVER_IP << 'ENDSSH'
    set -e
    
    # Create deployment directory
    sudo mkdir -p /opt/keelo
    sudo chown $USER:$USER /opt/keelo
    cd /opt/keelo
    
    # Copy files from temp
    cp /tmp/docker-compose.prod.yml ./docker-compose.yml
    cp /tmp/.env.production ./.env
    cp -r /tmp/nginx ./
    
    # Load Docker images
    echo "Loading Docker images..."
    docker load -i /tmp/keelo-frontend.tar
    docker load -i /tmp/keelo-backend.tar
    
    # Stop existing containers
    echo "Stopping existing containers..."
    docker-compose down || true
    
    # Start new containers
    echo "Starting new containers..."
    docker-compose up -d
    
    # Run database migrations
    echo "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head
    
    # Clean up
    rm /tmp/keelo-*.tar
    rm -rf /tmp/nginx
    
    # Check status
    docker-compose ps
    
    echo "Deployment complete!"
ENDSSH

# Step 5: Clean up local files
print_status "Cleaning up local files..."
rm keelo-frontend.tar keelo-backend.tar

print_status "Deployment completed successfully!"
print_status "Application should be available at https://$DOMAIN"

# Step 6: Health check
print_status "Running health check..."
sleep 10
if curl -f -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health | grep -q "200"; then
    print_status "Health check passed!"
else
    print_warning "Health check failed. Please check the deployment."
fi