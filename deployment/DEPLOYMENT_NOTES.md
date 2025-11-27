# 📝 Deployment Notes - IP and Domain Configuration

## 🌐 Access URLs

Your API is accessible via both IP address and domain:

### IP Access (HTTP)
- **API Base URL**: `http://209.38.89.74`
- **Example Endpoints**:
  - `http://209.38.89.74/api/auth/login/`
  - `http://209.38.89.74/api/users/`
  - `http://209.38.89.74/api/appointments/`

### Domain Access (HTTPS)
- **API Base URL**: `https://tailoredpsychology.com.au`
- **Example Endpoints**:
  - `https://tailoredpsychology.com.au/api/auth/login/`
  - `https://tailoredpsychology.com.au/api/users/`
  - `https://tailoredpsychology.com.au/api/appointments/`

## ⚙️ Configuration Details

### Nginx Configuration
- **IP Server Block**: Listens on port 80 (HTTP only)
  - Serves API directly via IP
  - No SSL required for IP access
  - Logs: `/var/log/nginx/psychology_clinic_ip_*.log`

- **Domain Server Block**: Listens on ports 80 and 443
  - HTTP redirects to HTTPS
  - SSL/TLS encryption enabled
  - Logs: `/var/log/nginx/psychology_clinic_*.log`

### Django Settings
- **ALLOWED_HOSTS** includes:
  - `209.38.89.74` (IP address)
  - `tailoredpsychology.com.au` (domain)
  - `www.tailoredpsychology.com.au` (www subdomain)

### Environment Variables
Make sure your `.env` file has:
```bash
ALLOWED_HOSTS=209.38.89.74,tailoredpsychology.com.au,www.tailoredpsychology.com.au
```

## 🔒 Security Considerations

### IP Access (HTTP)
- ✅ Suitable for API access
- ✅ No SSL certificate needed
- ⚠️ Data transmitted in plain text
- ⚠️ Use HTTPS for production if possible

### Domain Access (HTTPS)
- ✅ Encrypted connection
- ✅ SSL certificate required
- ✅ Recommended for production
- ✅ Better for web browsers

## 🧪 Testing

### Test IP Access
```bash
# Health check
curl http://209.38.89.74/health/

# API endpoint
curl http://209.38.89.74/api/auth/login/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Test Domain Access
```bash
# Health check
curl https://tailoredpsychology.com.au/health/

# API endpoint
curl https://tailoredpsychology.com.au/api/auth/login/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 📱 Frontend Configuration

### For React/Next.js Frontend

Update your API base URL based on environment:

```javascript
// .env.local (development)
NEXT_PUBLIC_API_URL=http://209.38.89.74

// .env.production (production)
NEXT_PUBLIC_API_URL=https://tailoredpsychology.com.au
```

Or use environment detection:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname === '209.38.89.74')
    ? 'http://209.38.89.74'
    : 'https://tailoredpsychology.com.au';
```

## 🔄 CORS Configuration

Make sure your Django CORS settings allow both:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://209.38.89.74",
    "https://tailoredpsychology.com.au",
    "https://www.tailoredpsychology.com.au",
    # Add your frontend URLs
]
```

## 📊 Monitoring

### Check Nginx Status
```bash
# Check both server blocks
sudo nginx -t
sudo systemctl status nginx

# View IP access logs
sudo tail -f /var/log/nginx/psychology_clinic_ip_access.log

# View domain access logs
sudo tail -f /var/log/nginx/psychology_clinic_access.log
```

### Check Django Logs
```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Check if IP is in ALLOWED_HOSTS
sudo -u www-data /var/www/clink-backend/venv/bin/python \
  /var/www/clink-backend/manage.py shell
>>> from django.conf import settings
>>> print(settings.ALLOWED_HOSTS)
```

## 🐛 Troubleshooting

### IP Access Not Working
1. Check firewall allows port 80:
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   ```

2. Check Nginx is listening:
   ```bash
   sudo netstat -tlnp | grep :80
   ```

3. Check Nginx configuration:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Domain SSL Issues
- IP access doesn't require SSL
- SSL only needed for domain access
- If SSL fails, IP will still work

### CORS Errors
- Make sure CORS_ALLOWED_ORIGINS includes your frontend URL
- Check if using IP or domain in frontend
- Verify CORS middleware is enabled

## 📝 Notes

- IP access is useful for:
  - Development and testing
  - Direct API access
  - Mobile app backend
  - Internal services

- Domain access is better for:
  - Production web applications
  - Browser-based access
  - SEO and branding
  - SSL/HTTPS security

