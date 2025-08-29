# Vercel Frontend Setup Guide

## Your Backend is Ready ✅
- Railway Backend URL: `https://growth-copilot-prod-production.up.railway.app`
- Status: Running and healthy

## Steps to Connect Frontend to Backend

### 1. Set Vercel Environment Variables

Go to your Vercel project settings and add these environment variables:

```bash
NEXT_PUBLIC_API_URL=https://growth-copilot-prod-production.up.railway.app
NEXT_PUBLIC_WS_URL=wss://growth-copilot-prod-production.up.railway.app/ws/chat
NEXT_PUBLIC_POSTHOG_KEY=phc_PLl6hIos5i2dPC5drTYHysJ16zIcfdAwVuiQE6tyGjx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 2. Deploy Frontend to Vercel

If not already deployed:

```bash
cd frontend
npm install
vercel
```

Or push to GitHub and connect to Vercel:

```bash
git add frontend/
git commit -m "Frontend ready for deployment"
git push origin master
```

### 3. Update CORS in Railway

Make sure your Railway backend has the correct CORS settings. Set this environment variable in Railway:

```bash
CORS_ORIGINS=["https://your-vercel-app.vercel.app", "https://yourdomain.com"]
```

Replace with your actual Vercel URL.

### 4. Test the Connection

Once deployed, test:
1. Open your Vercel app URL
2. Open browser console (F12)
3. Try to analyze a website
4. Check for WebSocket connection in Network tab

## Troubleshooting

If WebSocket doesn't connect:
- Check browser console for CORS errors
- Verify environment variables in Vercel dashboard
- Make sure Railway backend is running

If API calls fail:
- Check CORS_ORIGINS in Railway includes your Vercel URL
- Verify NEXT_PUBLIC_API_URL is correct
- Check browser console for specific errors