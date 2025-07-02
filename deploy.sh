#!/bin/bash

# AI Code Analysis Microservice - VM Deployment Script
# This script automates the deployment process on a virtual machine

set -e  # Exit on any error

echo "🚀 Starting AI Code Analysis Microservice deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_warning "Docker installed. You may need to log out and back in for group changes to take effect."
else
    print_status "Docker is already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    print_status "Docker Compose is already installed"
fi

# Create necessary directories
print_status "Creating application directories..."
mkdir -p logs data repo

# Set proper permissions
sudo chown -R $USER:$USER logs data repo

# Check if .env file exists
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before starting services"
    else
        print_error ".env.example not found. Please create .env file manually"
        exit 1
    fi
else
    print_status ".env file already exists"
fi

# Build and start services
print_status "Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check service status
print_status "Checking service status..."
docker-compose ps

# Test API endpoints
print_status "Testing API endpoints..."
if command -v curl &> /dev/null; then
    echo "Health check:"
    curl -s http://localhost:5000/health || print_warning "Health check failed - service may still be starting"
    echo ""
    echo "API documentation:"
    curl -s http://localhost:5000/docs || print_warning "API docs not available yet"
else
    print_warning "curl not available - cannot test endpoints"
fi

print_status "Deployment completed!"
echo ""
echo "📋 Service Information:"
echo "  - API URL: http://localhost:5000"
echo "  - API Docs: http://localhost:5000/docs"
echo "  - Health Check: http://localhost:5000/health"
echo ""
echo "🔧 Useful Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Update services: docker-compose pull && docker-compose up -d"
echo ""
print_status "Your AI Code Analysis Microservice is now running!" 