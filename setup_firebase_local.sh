#!/bin/bash

echo "Setting up Firebase Service Account for local development"

# Check if service account file exists
if [ ! -f "firebase-service-account.json" ]; then
    echo "❌ firebase-service-account.json not found!"
    echo "Please download it from Firebase Console:"
    echo "1. Go to https://console.firebase.google.com"
    echo "2. Select project: keelo-5924a"
    echo "3. Settings → Service accounts → Generate new private key"
    echo "4. Save as firebase-service-account.json in this directory"
    exit 1
fi

echo "✅ Found firebase-service-account.json"

# Read and minify the JSON (remove newlines and extra spaces)
SERVICE_ACCOUNT_JSON=$(cat firebase-service-account.json | jq -c .)

# Create a temporary .env.docker file
cat > .env.docker << EOF
FIREBASE_SERVICE_ACCOUNT_JSON='${SERVICE_ACCOUNT_JSON}'
EOF

echo "✅ Created .env.docker with Firebase credentials"

# Update docker-compose to use the env file
echo "Restarting backend with Firebase credentials..."
docker-compose --env-file .env.docker up -d backend

echo "✅ Backend restarted with Firebase Admin SDK"
echo ""
echo "Test it now at: http://localhost:3001/auth-debug"
echo ""
echo "⚠️  IMPORTANT: Don't commit firebase-service-account.json to git!"