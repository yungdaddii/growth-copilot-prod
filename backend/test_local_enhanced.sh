#!/bin/bash

# Test Enhanced NLP Locally
echo "================================"
echo "Testing Enhanced NLP Locally"
echo "================================"

# Set environment variable
export ENABLE_ENHANCED_NLP=true

# Check if Redis is running
echo "1. Checking Redis..."
redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running. Starting Redis..."
    redis-server --daemonize yes
fi

# Check if PostgreSQL is running
echo "2. Checking PostgreSQL..."
pg_isready > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL is running"
else
    echo "⚠️  PostgreSQL not running. Docker will provide it."
fi

# Test with Docker Compose
echo "3. Starting services with Docker Compose..."
cd /Users/edwardionel/Downloads/GrowthCopilot-1.0.0\ 2

# Stop any existing containers
docker-compose down

# Start with enhanced NLP enabled
echo "Starting with ENABLE_ENHANCED_NLP=true..."
ENABLE_ENHANCED_NLP=true docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check if backend is healthy
echo "4. Checking backend health..."
curl -s http://localhost:8000/health | jq .

# Check logs for enhanced NLP
echo "5. Checking if Enhanced NLP is active..."
docker-compose logs backend | grep -E "ENHANCED NLP|enhanced_nlp|Enhanced"

echo "================================"
echo "Test Complete!"
echo "================================"
echo ""
echo "To test manually:"
echo "1. Open http://localhost:3000"
echo "2. Send: 'analyze example.com'"
echo "3. Check if response is specific and detailed"
echo ""
echo "To view logs:"
echo "docker-compose logs -f backend"
echo ""
echo "To stop:"
echo "docker-compose down"