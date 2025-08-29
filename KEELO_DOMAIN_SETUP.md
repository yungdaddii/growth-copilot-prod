# Setting up keelo.ai Domain with Vercel

## Step 1: Add Domain to Vercel

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Select your `frontend` project
3. Go to **Settings** → **Domains**
4. Click **Add Domain**
5. Enter: `keelo.ai`
6. Click **Add**

Vercel will show you one of two options:

## Option A: If You Own keelo.ai (Recommended)

### Add these DNS records to your domain provider (GoDaddy, Namecheap, etc.):

**For root domain (keelo.ai):**
- Type: `A`
- Name: `@`
- Value: `76.76.21.21`

**For www subdomain (www.keelo.ai):**
- Type: `CNAME`
- Name: `www`
- Value: `cname.vercel-dns.com`

### Where to add DNS records:

1. **GoDaddy**: 
   - Login → My Products → DNS → Manage DNS
   
2. **Namecheap**: 
   - Dashboard → Domain List → Manage → Advanced DNS

3. **Cloudflare**: 
   - Dashboard → Select domain → DNS

## Option B: If Using Vercel's Nameservers

Change your domain's nameservers to:
- `ns1.vercel-dns.com`
- `ns2.vercel-dns.com`

## Step 2: Wait for Propagation

- DNS changes can take 5 minutes to 48 hours (usually under 1 hour)
- Vercel will automatically provision SSL certificate

## Step 3: Update Your App Configuration

Once domain is connected, update these:

### In Vercel Environment Variables:
```
NEXT_PUBLIC_APP_URL=https://keelo.ai
```

### In Railway Environment Variables:
Update CORS_ORIGINS to include:
```
["https://keelo.ai", "https://www.keelo.ai", "https://frontend-six-psi-49.vercel.app", "http://localhost:3000"]
```

## Step 4: Test Your Domain

1. Visit https://keelo.ai
2. Check SSL certificate (should show "Issued by Let's Encrypt")
3. Test the app functionality

## Troubleshooting

If domain doesn't work after 1 hour:
1. Check DNS propagation: https://dnschecker.org
2. Verify records in Vercel dashboard (should show green checkmarks)
3. Clear browser cache and try incognito mode

## Current Setup Status

- ✅ Vercel app deployed at: `frontend-six-psi-49.vercel.app`
- ⏳ Custom domain: `keelo.ai` (needs configuration)
- ✅ SSL: Will be auto-provisioned by Vercel
- ✅ Backend: Connected via Railway