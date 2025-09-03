# Update Vercel Environment Variables

## Steps to Update Vercel:

1. **Go to Vercel Dashboard**
   - https://vercel.com
   - Select your project

2. **Go to Settings → Environment Variables**

3. **Add/Update these variables for Production:**

```
NEXT_PUBLIC_API_URL = https://growth-copilot-prod-production.up.railway.app
NEXT_PUBLIC_WS_URL = wss://growth-copilot-prod-production.up.railway.app/ws/chat
```

4. **Keep your existing Firebase variables:**
```
NEXT_PUBLIC_FIREBASE_API_KEY = AIzaSyCgmwHYJ1m3bqxWfnf29c8SSTtzyfWH74Q
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN = keelo-5924a.firebaseapp.com
NEXT_PUBLIC_FIREBASE_DATABASE_URL = https://keelo-5924a-default-rtdb.firebaseio.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID = keelo-5924a
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = keelo-5924a.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = 146204271487
NEXT_PUBLIC_FIREBASE_APP_ID = 1:146204271487:web:76aa00c87a940ba2aef04a
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID = G-VLB1J1F72L
```

5. **Redeploy**
   - After updating environment variables, trigger a redeploy
   - Go to Deployments tab → Click three dots on latest → Redeploy

## Test Your Production Site:

Once redeployed, test your production chat:
1. Go to your Vercel URL
2. Try "analyze stripe.com" in the chat
3. You should get responses now!

## Success Confirmation:

✅ Railway backend is working (WebSocket test passed)
✅ Database migration completed on Supabase
✅ Environment variables updated for production

The chat should now work on your production site!