#!/bin/bash

echo "🚀 Starting Growth Co-pilot locally..."
echo "================================"

# Go to main directory
cd "/Users/edwardionel/Downloads/GrowthCopilot-1.0.0 2"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first!"
    exit 1
fi

echo "✅ Docker is running"

# Stop any existing containers
echo "🧹 Cleaning up old containers..."
docker-compose down

# Start all services
echo "🔧 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if backend is responding
echo "🔍 Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend failed to start. Check logs with: docker-compose logs backend"
    exit 1
fi

# Check if frontend is responding
echo "🔍 Checking frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "⚠️  Frontend may still be building. Check logs with: docker-compose logs frontend"
fi

echo ""
echo "================================"
echo "🎉 Growth Co-pilot is running!"
echo "================================"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo ""
echo "🧪 Test by:"
echo "  1. Opening http://localhost:3000"
echo "  2. Enter a domain like 'stripe.com'"
echo "  3. Press Enter to analyze"