# 🔧 DNS Fix: Can't Delete CNAME Record

## Problem
You have a CNAME record for `www` pointing to App Platform that you can't delete.

## Solution: Change CNAME Instead of Delete

If you can't delete the CNAME, **change it** to point to your root domain instead.

### Step 1: Edit the CNAME Record

1. Find the CNAME record:
   ```
   Type: CNAME
   Hostname: www
   Value: hammerhead-app-vup4g.ondigitalocean.app
   ```

2. Click **Edit** (pencil icon) or click on the record

3. Change the value from:
   ```
   hammerhead-app-vup4g.ondigitalocean.app
   ```
   
   To:
   ```
   tailoredpsychology.com.au
   ```

4. Save the changes

### Step 2: Verify

After changing, your DNS should look like:

```
Type    Hostname    Value
─────────────────────────────────────────────
A       @           209.38.89.74
CNAME   www         tailoredpsychology.com.au  ← Changed this!
NS      @           ns1.digitalocean.com
NS      @           ns2.digitalocean.com
NS      @           ns3.digitalocean.com
```

## How This Works

- The A record for `@` points `tailoredpsychology.com.au` → `209.38.89.74`
- The CNAME for `www` makes `www.tailoredpsychology.com.au` an alias of `tailoredpsychology.com.au`
- So `www.tailoredpsychology.com.au` will resolve to `209.38.89.74` (via the A record)

## Alternative: Contact Support

If you still can't edit or delete:
1. Go to DigitalOcean Support
2. Ask them to delete the CNAME record for `www.tailoredpsychology.com.au`
3. Or ask them to change it to point to `tailoredpsychology.com.au`

## Why This Happens

Sometimes DNS records get "stuck" or the interface doesn't show delete options. Changing the CNAME to point to your root domain achieves the same result.

