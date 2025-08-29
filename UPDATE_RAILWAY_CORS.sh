#!/bin/bash

# Update Railway environment variable for CORS

echo "Setting CORS_ORIGINS in Railway..."

railway variables --set CORS_ORIGINS='["https://frontend-six-psi-49.vercel.app", "http://localhost:3000"]'

echo "✅ CORS_ORIGINS updated!"
echo ""
echo "Railway will automatically redeploy with the new settings."
echo "Your Vercel frontend at https://frontend-six-psi-49.vercel.app can now connect to the Railway backend!"