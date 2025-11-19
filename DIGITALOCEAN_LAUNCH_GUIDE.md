# 🚀 DigitalOcean Full Launch Guide - Step by Step

Complete guide for launching your Psychology Clinic system on DigitalOcean. No code - just what to buy and configure.

---

## 📋 What You Need to Buy & Set Up

### 1. DigitalOcean Account Setup

**Step 1: Create Account**
- Go to [digitalocean.com](https://www.digitalocean.com)
- Sign up for an account
- Verify your email address
- Add payment method (credit card)

**Step 2: Choose Region**
- Select **Sydney (syd1)** - Australian data center
- This ensures all data stays in Australia (compliance requirement)

---

## 💰 Services to Purchase

### Essential Services (Required)

#### 1. **Droplet (Server) - $24/month**
**What it is:** Your main server where the backend runs

**What to buy:**
- **Type:** Basic Droplet
- **Plan:** $24/month (4GB RAM, 2 vCPU, 80GB SSD)
- **Region:** Sydney (syd1)
- **Image:** Ubuntu 22.04 LTS
- **Authentication:** SSH keys (recommended) or password

**Why this size:** Good balance of performance and cost. Can upgrade later if needed.

---

#### 2. **Managed PostgreSQL Database - $60/month**
**What it is:** Your database where all patient data is stored

**What to buy:**
- **Type:** Managed Database
- **Engine:** PostgreSQL 15 or 16
- **Plan:** Basic $60/month (2GB RAM, 1 vCPU, 25GB storage)
- **Region:** Sydney (syd1)
- **Important:** Enable "Encryption at rest" ✅ (required for compliance)

**Why this size:** Enough for thousands of patients. Can scale up later.

---

#### 3. **Managed Redis - $30/month**
**What it is:** Used for background tasks (appointment reminders, compliance checks)

**What to buy:**
- **Type:** Managed Database
- **Engine:** Redis 7
- **Plan:** Basic $30/month (2GB RAM)
- **Region:** Sydney (syd1)
- **Important:** Enable "Persistence" ✅

**Why this size:** Sufficient for background task processing.

---

#### 4. **Spaces (File Storage) - $5/month**
**What it is:** Cloud storage for files (insurance certificates, documents, images)

**What to buy:**
- **Type:** Spaces
- **Plan:** $5/month (250GB storage)
- **Region:** Sydney (syd1)
- **Important:** Enable "File versioning" ✅
- **CDN:** Enable CDN (included, no extra cost)

**Why this size:** 250GB is plenty for documents and images.

---

### Optional but Recommended

#### 5. **Domain Name - ~$15/year**
**What it is:** Your website address (e.g., yourclinic.com.au)

**Where to buy:**
- **VentraIP** (recommended for .com.au)
- **Crazy Domains**
- **GoDaddy Australia**

**What to buy:**
- **Extension:** `.com.au` (requires ABN/ACN) or `.au` (no ABN needed)
- **Cost:** ~$15-25 per year

**Note:** You need an ABN (Australian Business Number) for `.com.au` domains.

---

#### 6. **Cloudflare (Free)**
**What it is:** CDN, DDoS protection, free SSL certificates

**What to do:**
- Sign up at [cloudflare.com](https://www.cloudflare.com) (free account)
- Add your domain
- Update nameservers at your domain registrar
- Enable "Always Use HTTPS"
- Enable "Auto Minify"

**Cost:** FREE

---

## 📊 Total Monthly Cost

| Service | Monthly Cost (AUD) |
|---------|-------------------|
| Droplet (Server) | $36 |
| Managed PostgreSQL | $90 |
| Managed Redis | $45 |
| Spaces (File Storage) | $5 |
| Domain (annual) | ~$1.25/month |
| Cloudflare | $0 |
| **TOTAL** | **~$177/month** |

**First Month:** May be slightly higher due to domain purchase.

---

## 🔧 Setup Steps (What to Configure)

### Step 1: Create Droplet (Server)

1. **In DigitalOcean Dashboard:**
   - Click "Create" → "Droplets"
   - Choose "Ubuntu 22.04 LTS"
   - Select "Basic" plan → $24/month
   - Choose "Sydney" region
   - Add SSH key (or use password)
   - Give it a name: "psychology-clinic-backend"
   - Click "Create Droplet"

2. **Wait 1-2 minutes** for droplet to be created

3. **Note down:**
   - IP address (you'll need this)
   - Root password (if you used password auth)

---

### Step 2: Create Managed PostgreSQL Database

1. **In DigitalOcean Dashboard:**
   - Click "Create" → "Databases"
   - Choose "PostgreSQL"
   - Select version 15 or 16
   - Choose "Basic" plan → $60/month
   - Choose "Sydney" region
   - **IMPORTANT:** Enable "Encryption at rest" ✅
   - Give it a name: "psychology-clinic-db"
   - Click "Create Database Cluster"

2. **Wait 3-5 minutes** for database to be created

3. **After creation:**
   - Go to database settings
   - Note down:
     - **Host** (database hostname)
     - **Port** (usually 25060)
     - **Database name** (default: defaultdb)
     - **Username** (default: doadmin)
     - **Password** (click "Show" to see it)

4. **Connection Settings:**
   - Go to "Users & Databases" tab
   - Create a new database: "psychology_clinic"
   - Note down the connection string (you'll need this)

---

### Step 3: Create Managed Redis

1. **In DigitalOcean Dashboard:**
   - Click "Create" → "Databases"
   - Choose "Redis"
   - Select version 7
   - Choose "Basic" plan → $30/month
   - Choose "Sydney" region
   - **IMPORTANT:** Enable "Persistence" ✅
   - Give it a name: "psychology-clinic-redis"
   - Click "Create Database Cluster"

2. **Wait 3-5 minutes** for Redis to be created

3. **After creation:**
   - Note down:
     - **Host** (Redis hostname)
     - **Port** (usually 25061)
     - **Password** (click "Show" to see it)

---

### Step 4: Create Spaces (File Storage)

1. **In DigitalOcean Dashboard:**
   - Click "Create" → "Spaces"
   - Choose "Sydney" region
   - Give it a name: "psychology-clinic-files"
   - **IMPORTANT:** Enable "File versioning" ✅
   - **IMPORTANT:** Enable "CDN" ✅
   - Click "Create a Space"

2. **After creation:**
   - Go to "Settings" tab
   - Note down:
     - **Endpoint** (e.g., syd1.digitaloceanspaces.com)
     - **Access Key** (create one in "API Keys" section)
     - **Secret Key** (save this securely!)

---

### Step 5: Domain Setup

1. **Buy Domain:**
   - Go to domain registrar (VentraIP, Crazy Domains, etc.)
   - Search for your desired domain (e.g., yourclinic.com.au)
   - Purchase domain
   - Complete registration (may need ABN for .com.au)

2. **Set Up DNS:**
   - **Option A: Use Cloudflare (Recommended)**
     - Sign up at cloudflare.com
     - Add your domain
     - Cloudflare will give you nameservers
     - Update nameservers at your domain registrar
     - Add DNS records in Cloudflare:
       - A record: `@` → Your Droplet IP
       - A record: `www` → Your Droplet IP
       - CNAME: `api` → `yourclinic.com.au`
   
   - **Option B: Use DigitalOcean DNS**
     - In DigitalOcean, go to "Networking" → "Domains"
     - Add your domain
     - Add DNS records:
       - A record: `@` → Your Droplet IP
       - A record: `www` → Your Droplet IP

---

### Step 6: SSL Certificate (HTTPS)

**If using Cloudflare:**
- SSL is automatic and free
- Just enable "Always Use HTTPS" in Cloudflare settings

**If NOT using Cloudflare:**
- You'll need to install Let's Encrypt on your server
- (This requires server access - your developer will handle this)

---

## 🔐 Security Configuration

### Firewall Setup (DigitalOcean)

1. **In DigitalOcean Dashboard:**
   - Go to "Networking" → "Firewalls"
   - Click "Create Firewall"
   - Name: "psychology-clinic-firewall"
   - Add rules:
     - **Inbound:**
       - HTTP (port 80) - Allow
       - HTTPS (port 443) - Allow
       - SSH (port 22) - Allow (only from your IP)
     - **Outbound:**
       - All traffic - Allow
   - Attach to your Droplet

### Database Firewall

1. **For PostgreSQL:**
   - Go to your database → "Settings" → "Trusted Sources"
   - Add your Droplet IP address
   - This allows your server to connect to the database

2. **For Redis:**
   - Same process - add Droplet IP to trusted sources

---

## 📝 Information You Need to Collect

Create a document with all these details:

### Server (Droplet)
- [ ] IP Address: ________________
- [ ] Root password (if used): ________________
- [ ] SSH key location: ________________

### Database (PostgreSQL)
- [ ] Host: ________________
- [ ] Port: ________________
- [ ] Database name: ________________
- [ ] Username: ________________
- [ ] Password: ________________
- [ ] Connection string: ________________

### Redis
- [ ] Host: ________________
- [ ] Port: ________________
- [ ] Password: ________________
- [ ] Connection string: ________________

### Spaces (File Storage)
- [ ] Space name: ________________
- [ ] Endpoint: ________________
- [ ] Access Key: ________________
- [ ] Secret Key: ________________
- [ ] CDN endpoint: ________________

### Domain
- [ ] Domain name: ________________
- [ ] Nameservers: ________________
- [ ] DNS provider: ________________

### Cloudflare (if used)
- [ ] Account email: ________________
- [ ] API token: ________________

---

## ✅ Pre-Launch Checklist

### DigitalOcean Services
- [ ] Droplet created and running
- [ ] PostgreSQL database created with encryption enabled
- [ ] Redis created with persistence enabled
- [ ] Spaces created with versioning and CDN enabled
- [ ] Firewall configured and attached to Droplet
- [ ] Database firewall allows Droplet IP

### Domain & DNS
- [ ] Domain purchased
- [ ] DNS configured (Cloudflare or DigitalOcean)
- [ ] A records pointing to Droplet IP
- [ ] SSL certificate configured (Cloudflare or Let's Encrypt)

### Information Collected
- [ ] All connection strings saved securely
- [ ] All passwords saved securely
- [ ] All IP addresses noted
- [ ] All endpoints documented

### Security
- [ ] Firewall rules configured
- [ ] Database access restricted to Droplet IP
- [ ] Strong passwords set for all services
- [ ] SSH keys configured (if using)

---

## 🚀 Next Steps After Setup

Once all services are purchased and configured:

1. **Give Information to Developer:**
   - Share all connection strings and credentials securely
   - Developer will deploy the backend code to the Droplet
   - Developer will configure the application with database, Redis, and Spaces

2. **Frontend Deployment:**
   - Your frontend can be deployed to:
     - Vercel (free tier available)
     - Netlify (free tier available)
     - Another DigitalOcean Droplet
   - Frontend will connect to your backend API

3. **Testing:**
   - Test all features in production environment
   - Verify SSL certificate is working
   - Test database connections
   - Test file uploads to Spaces

4. **Go Live:**
   - Once testing is complete, you're ready to launch!

---

## 💡 Tips & Recommendations

### Cost Optimization
- Start with the recommended sizes - you can always upgrade later
- Monitor usage in DigitalOcean dashboard
- Set up billing alerts to avoid surprises

### Security Best Practices
- Use SSH keys instead of passwords
- Enable two-factor authentication on DigitalOcean account
- Regularly update server software
- Keep backups enabled

### Scaling Up
- If you need more resources, you can upgrade any service with one click
- No downtime required for most upgrades
- Monitor performance and scale as needed

### Support
- DigitalOcean has excellent documentation
- Community support forums available
- Paid support plans available if needed

---

## 📞 Support Resources

- **DigitalOcean Documentation:** [docs.digitalocean.com](https://docs.digitalocean.com)
- **DigitalOcean Community:** [digitalocean.com/community](https://www.digitalocean.com/community)
- **DigitalOcean Support:** Available in dashboard

---

## 🎯 Summary

**What to Buy:**
1. DigitalOcean Droplet ($36/month)
2. Managed PostgreSQL ($90/month)
3. Managed Redis ($45/month)
4. Spaces Storage ($5/month)
5. Domain name (~$15/year)
6. Cloudflare account (FREE)

**Total:** ~$177/month

**What to Configure:**
1. Create all services in DigitalOcean
2. Set up domain and DNS
3. Configure firewalls
4. Collect all connection information
5. Give information to developer for deployment

**Time Required:** 1-2 hours for setup

---

**Ready to Launch!** 🚀

Once all services are set up and configured, your developer can deploy the application and you'll be ready to go live!

---

**Last Updated:** November 2025

