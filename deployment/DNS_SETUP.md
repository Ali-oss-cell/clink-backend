# 🌐 DNS Configuration for DigitalOcean Droplet

## Current DNS Records (App Platform)
You currently have:
- `www.tailoredpsychology.com.au` → CNAME → `hammerhead-app-vup4g.ondigitalocean.app` (App Platform)
- NS records pointing to DigitalOcean

## Required DNS Records (Droplet)

Since you're switching from App Platform to Droplet, you need to update your DNS records.

### Step 1: Access DigitalOcean DNS

1. Go to [DigitalOcean Dashboard](https://cloud.digitalocean.com/)
2. Click **Networking** → **Domains**
3. Click on **tailoredpsychology.com.au**

### Step 2: Remove/Update Existing Records

**Remove or update:**
- ❌ Delete: `www` CNAME pointing to `hammerhead-app-vup4g.ondigitalocean.app`

### Step 3: Add New A Records

Add these **A records** pointing to your Droplet IP `209.38.89.74`:

#### Record 1: Root Domain
```
Type: A
Hostname: @ (or leave blank)
Will Direct To: 209.38.89.74
TTL: 3600 (or 1800)
```

#### Record 2: WWW Subdomain
```
Type: A
Hostname: www
Will Direct To: 209.38.89.74
TTL: 3600 (or 1800)
```

**OR** use CNAME for www (alternative):
```
Type: CNAME
Hostname: www
Is an alias of: tailoredpsychology.com.au
TTL: 3600 (or 1800)
```

### Step 4: Keep NS Records

**Keep these NS records** (don't change):
```
Type: NS
Hostname: @
Directs to: ns1.digitalocean.com
TTL: 1800

Type: NS
Hostname: @
Directs to: ns2.digitalocean.com
TTL: 1800

Type: NS
Hostname: @
Directs to: ns3.digitalocean.com
TTL: 1800
```

## Final DNS Configuration

After changes, your DNS records should look like:

```
Type    Hostname    Value
─────────────────────────────────────────────
A       @           209.38.89.74
A       www         209.38.89.74
NS      @           ns1.digitalocean.com
NS      @           ns2.digitalocean.com
NS      @           ns3.digitalocean.com
```

## DNS Propagation

- **TTL**: 1800 seconds (30 minutes) or 3600 seconds (1 hour)
- **Propagation Time**: Usually 5-30 minutes, can take up to 48 hours
- **Check DNS**: Use [whatsmydns.net](https://www.whatsmydns.net/) to check propagation

## Verification

After updating DNS, verify with:

```bash
# Check root domain
dig tailoredpsychology.com.au +short
# Should return: 209.38.89.74

# Check www subdomain
dig www.tailoredpsychology.com.au +short
# Should return: 209.38.89.74

# Check from your computer
nslookup tailoredpsychology.com.au
nslookup www.tailoredpsychology.com.au
```

## Important Notes

1. **Remove App Platform CNAME**: The old CNAME to App Platform must be deleted
2. **Use A Records**: A records are better for root domain and www
3. **Wait for Propagation**: DNS changes can take time to propagate
4. **SSL Certificate**: After DNS propagates, you can set up SSL with Let's Encrypt

## Troubleshooting

### DNS Not Updating?
- Wait 30-60 minutes for propagation
- Clear your DNS cache: `sudo systemd-resolve --flush-caches` (Linux) or `ipconfig /flushdns` (Windows)
- Check from different location: [whatsmydns.net](https://www.whatsmydns.net/)

### Still Pointing to App Platform?
- Make sure you deleted the CNAME record
- Check if there are multiple DNS providers (GoDaddy might have old records)
- Verify NS records point to DigitalOcean

### Can't Access via Domain?
- Check if A records are correct (should point to 209.38.89.74)
- Verify Nginx is running: `sudo systemctl status nginx`
- Check firewall allows ports 80 and 443
- Test IP directly: `http://209.38.89.74` (should work immediately)

