# 🌐 DNS Configuration: Frontend (App Platform) + Backend (Droplet)

## Architecture

- **Frontend**: App Platform (React/Next.js) → `tailoredpsychology.com.au`
- **Backend API**: Droplet (Django) → `209.38.89.74` or `api.tailoredpsychology.com.au`

## Recommended DNS Setup

### Option 1: Root Domain for Frontend, Subdomain for API (Recommended)

```
Type    Hostname    Value
─────────────────────────────────────────────────────────────
A       @           209.38.89.74                    ← Backend (or remove if using subdomain)
CNAME   www         tailoredpsychology.com.au        ← Frontend
CNAME   api         hammerhead-app-vup4g.ondigitalocean.app  ← Backend API
NS      @           ns1.digitalocean.com
NS      @           ns2.digitalocean.com
NS      @           ns3.digitalocean.com
```

**OR** if you want frontend on root domain:

### Option 2: Root Domain for Frontend, IP for API

```
Type    Hostname    Value
─────────────────────────────────────────────────────────────
CNAME   @           hammerhead-app-vup4g.ondigitalocean.app   ← Frontend
CNAME   www         hammerhead-app-vup4g.ondigitalocean.app  ← Frontend
A       api         209.38.89.74                            ← Backend API
NS      @           ns1.digitalocean.com
NS      @           ns2.digitalocean.com
NS      @           ns3.digitalocean.com
```

## Current Setup Analysis

Based on your current DNS:
- ✅ `tailoredpsychology.com.au` → `209.38.89.74` (A record) - Points to Droplet
- ✅ `www.tailoredpsychology.com.au` → `tailoredpsychology.com.au` (CNAME) - Also points to Droplet

**Problem**: Both root and www point to your Droplet (backend), but you need frontend on App Platform.

## Solution: Update DNS for Frontend + Backend

### Recommended Configuration

1. **Change root domain to point to App Platform** (for frontend):
   ```
   Type: CNAME (or A if App Platform provides IP)
   Hostname: @
   Value: hammerhead-app-vup4g.ondigitalocean.app
   ```

2. **Keep www pointing to root** (frontend):
   ```
   Type: CNAME
   Hostname: www
   Value: tailoredpsychology.com.au
   ```

3. **Add API subdomain** (for backend):
   ```
   Type: A
   Hostname: api
   Value: 209.38.89.74
   ```

## Final DNS Configuration

```
Type    Hostname    Value
─────────────────────────────────────────────────────────────
CNAME   @           hammerhead-app-vup4g.ondigitalocean.app   ← Frontend
CNAME   www         tailoredpsychology.com.au                 ← Frontend (via root)
A       api         209.38.89.74                             ← Backend API
NS      @           ns1.digitalocean.com
NS      @           ns2.digitalocean.com
NS      @           ns3.digitalocean.com
```

## Frontend Configuration

In your React/Next.js frontend, set the API URL:

```typescript
// .env.local or .env.production
NEXT_PUBLIC_API_URL=https://api.tailoredpsychology.com.au
// OR use IP directly:
NEXT_PUBLIC_API_URL=http://209.38.89.74
```

## Backend Configuration

Update your Nginx config to handle the API subdomain:

```nginx
# API subdomain
server {
    listen 80;
    server_name api.tailoredpsychology.com.au;
    
    location / {
        proxy_pass http://unix:/var/www/clink-backend/gunicorn.sock;
        # ... rest of config
    }
}
```

## Alternative: Use IP for API

If you don't want to set up a subdomain, just use the IP directly:

```typescript
// Frontend .env
NEXT_PUBLIC_API_URL=http://209.38.89.74
```

## Summary

**What to change:**
1. ✅ Keep `www` CNAME pointing to root (already correct)
2. ❌ Change root domain A record to CNAME pointing to App Platform
3. ✅ Add `api` subdomain A record pointing to `209.38.89.74` (optional)

**Result:**
- `tailoredpsychology.com.au` → Frontend (App Platform)
- `www.tailoredpsychology.com.au` → Frontend (App Platform)
- `api.tailoredpsychology.com.au` → Backend API (Droplet)
- `209.38.89.74` → Backend API (Direct IP access)

