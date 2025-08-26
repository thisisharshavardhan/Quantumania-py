#!/bin/bash

echo "🚀 Starting Quantumania-py Production Server..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the Quantumania-py root directory"
    exit 1
fi

# Activate virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install/update dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example"
    cp .env.example .env
    echo "❗ Please edit .env file with your IBM Quantum token before running again!"
    exit 1
fi

# Start Redis if not running
if ! pgrep redis-server > /dev/null; then
    echo "🔄 Starting Redis..."
    sudo systemctl start redis-server
fi

# Build frontend
echo "🏗️  Building frontend..."
cd frontend_shadcn
npm install
npm run build
cd ..

# Start services
echo "🚀 Starting services..."
sudo systemctl start quantumania-api
sudo systemctl start quantumania-celery
sudo systemctl restart nginx

echo "✅ Quantumania-py is now running!"
echo "🌐 Frontend: http://your_vps_ip"
echo "🔗 API: http://your_vps_ip/api/v1/dashboard"
echo "📊 API Docs: http://your_vps_ip:8000/docs"

# Show service status
echo "📋 Service Status:"
sudo systemctl status quantumania-api --no-pager -l
sudo systemctl status quantumania-celery --no-pager -l
