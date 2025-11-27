# 🔧 Solution: Can't Delete Duplicate A Record

## Problem
You have two A records for the root domain:
- `tailoredpsychology.com.au` → `162.159.140.98` (App Platform - frontend)
- `tailoredpsychology.com.au` → `209.38.89.74` (Droplet - backend)

You can't delete the second one, causing DNS conflicts.

## Solution: Configure Backend to Ignore Root Domain

The backend Nginx is now configured to **only respond to**:
1. ✅ IP address: `209.38.89.74`
2. ✅ API subdomain: `api.tailoredpsychology.com.au`
3. ❌ Root domain: `tailoredpsychology.com.au` (ignored)

## How It Works

1. **DNS Resolution**: 
   - DNS may return either IP (`162.159.140.98` or `209.38.89.74`)
   - If it returns App Platform IP → Frontend serves the request ✅
   - If it returns Droplet IP → Nginx ignores it (no server block matches) → Request fails/timeouts

2. **Backend Access**:
   - ✅ `http://209.38.89.74` → Works (direct IP)
   - ✅ `http://api.tailoredpsychology.com.au` → Works (API subdomain)
   - ❌ `http://tailoredpsychology.com.au` → Won't work on backend (by design)

3. **Frontend Access**:
   - ✅ `https://tailoredpsychology.com.au` → Works (App Platform)
   - ✅ `https://www.tailoredpsychology.com.au` → Works (App Platform)

## Alternative Solutions

### Option 1: Contact DigitalOcean Support
Ask them to delete the A record pointing to `209.38.89.74`:
- Go to: https://cloud.digitalocean.com/support
- Create a ticket asking to delete the duplicate A record

### Option 2: Use API Subdomain Only
Configure your frontend to always use:
- `http://api.tailoredpsychology.com.au` for API calls
- Or `http://209.38.89.74` directly

### Option 3: Wait for DNS to Prefer App Platform
Sometimes DNS providers will prefer one record over another. You can test which one resolves more often.

## Current Configuration

Your backend Nginx will:
- ✅ Respond to: `209.38.89.74` (IP)
- ✅ Respond to: `api.tailoredpsychology.com.au` (API subdomain)
- ❌ Ignore: `tailoredpsychology.com.au` (root domain - no matching server block)

## Frontend Configuration

In your React/Next.js app, use:

```typescript
// .env.production
NEXT_PUBLIC_API_URL=http://api.tailoredpsychology.com.au
// OR
NEXT_PUBLIC_API_URL=http://209.38.89.74
```

## Testing

Test your setup:

```bash
# Backend via IP (should work)
curl http://209.38.89.74/health/

# Backend via API subdomain (should work)
curl http://api.tailoredpsychology.com.au/health/

# Root domain (may or may not work - depends on DNS)
curl http://tailoredpsychology.com.au/health/
# This should fail or timeout if DNS returns backend IP
```

## Summary

Even though you can't delete the duplicate A record, the backend is configured to ignore root domain requests. This means:
- Frontend will work on root domain (App Platform)
- Backend will work on IP and API subdomain
- No conflicts in serving content

The duplicate A record is not ideal, but this configuration makes it work safely.

