#!/bin/bash

echo "🔍 Checking disk space..."

# Check disk usage
echo "📊 Current disk usage:"
df -h

echo ""
echo "🗑️  Cleaning up Docker (if installed):"
if command -v docker &> /dev/null; then
    echo "Cleaning unused Docker images..."
    docker system prune -f
    echo "Cleaning unused Docker volumes..."
    docker volume prune -f
else
    echo "Docker not installed"
fi

echo ""
echo "🧹 Cleaning package cache:"
sudo apt clean
sudo apt autoremove -y

echo ""
echo "📦 Checking largest directories:"
du -h --max-depth=1 / 2>/dev/null | sort -hr | head -10

echo ""
echo "💡 Recommendations:"
echo "1. If you have less than 5GB free space, consider:"
echo "   - Upgrading your VM disk size"
echo "   - Using the minimal requirements (requirements-minimal.txt)"
echo "   - Installing packages one by one"
echo ""
echo "2. To use minimal requirements:"
echo "   cp requirements-minimal.txt requirements.txt"
echo "   docker-compose build" 