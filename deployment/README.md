# 🚀 Deployment Configuration Files

This directory contains all the configuration files needed to deploy the Psychology Clinic Backend to a DigitalOcean Droplet.

## 📁 Files

### Service Files
- **gunicorn.service** - Systemd service file for Gunicorn (Django WSGI server)
- **celery.service** - Systemd service file for Celery worker (background tasks)
- **celery-beat.service** - Systemd service file for Celery Beat (scheduled tasks)

### Configuration Files
- **nginx.conf** - Nginx reverse proxy configuration with SSL support

### Scripts
- **../deploy.sh** - Complete deployment automation script

## 🔧 Usage

### Quick Deployment

1. **Prepare your server:**
   ```bash
   # On your DigitalOcean Droplet
   sudo apt update && sudo apt upgrade -y
   ```

2. **Upload your code:**
   ```bash
   # Option 1: Clone from Git
   cd /var/www
   sudo git clone https://github.com/yourusername/clink-backend.git
   cd clink-backend
   
   # Option 2: Upload via SCP
   scp -r . user@your-droplet-ip:/var/www/clink-backend
   ```

3. **Run deployment script:**
   ```bash
   cd /var/www/clink-backend
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Manual Setup

If you prefer manual setup, follow these steps:

#### 1. Install Gunicorn Service
```bash
sudo cp deployment/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

#### 2. Install Celery Services
```bash
sudo cp deployment/celery.service /etc/systemd/system/
sudo cp deployment/celery-beat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable celery celery-beat
sudo systemctl start celery celery-beat
```

#### 3. Configure Nginx
```bash
sudo cp deployment/nginx.conf /etc/nginx/sites-available/psychology_clinic
sudo ln -s /etc/nginx/sites-available/psychology_clinic /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Setup SSL
```bash
sudo certbot --nginx -d tailoredpsychology.com.au -d www.tailoredpsychology.com.au
```

## 🔍 Service Management

### Check Status
```bash
sudo systemctl status gunicorn
sudo systemctl status celery
sudo systemctl status celery-beat
sudo systemctl status nginx
```

### View Logs
```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Celery worker logs
sudo tail -f /var/log/celery/worker.log

# Celery Beat logs
sudo tail -f /var/log/celery/beat.log

# Nginx logs
sudo tail -f /var/log/nginx/psychology_clinic_error.log
```

### Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat
sudo systemctl restart nginx
```

## ⚙️ Configuration

### Update Application Path

If your application is in a different location, update these files:
- `gunicorn.service` - Change `WorkingDirectory` and `ExecStart` paths
- `celery.service` - Change `WorkingDirectory` and `ExecStart` paths
- `celery-beat.service` - Change `WorkingDirectory` and `ExecStart` paths
- `nginx.conf` - Update paths in `location /static/` and `location /media/`

### Update Domain

Edit `nginx.conf` and replace:
- `tailoredpsychology.com.au` with your domain
- Update SSL certificate paths if needed

### Gunicorn Workers

Adjust the number of workers in `gunicorn.service`:
```ini
--workers 3  # Change based on: (2 x CPU cores) + 1
```

For 2 CPUs: `--workers 5` is optimal.

## 🔒 Security Notes

- All services run as `www-data` user (non-root)
- Environment variables loaded from `.env` file
- SSL/TLS encryption configured
- Security headers enabled in Nginx
- Firewall should allow only ports 22, 80, 443

## 📝 Environment Variables

Make sure your `.env` file contains:
- `SECRET_KEY` - Django secret key
- `DEBUG=False` - Production mode
- `ALLOWED_HOSTS` - Your domain
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- All API keys (Twilio, Stripe, SendGrid, etc.)

## 🐛 Troubleshooting

### Gunicorn won't start
```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Check permissions
sudo chown -R www-data:www-data /var/www/clink-backend
```

### Celery not processing tasks
```bash
# Check Redis is running
sudo systemctl status redis

# Check Celery logs
sudo tail -f /var/log/celery/worker.log
```

### Nginx 502 Bad Gateway
```bash
# Check Gunicorn is running
sudo systemctl status gunicorn

# Check socket file exists
ls -la /var/www/clink-backend/gunicorn.sock

# Check permissions
sudo chown www-data:www-data /var/www/clink-backend/gunicorn.sock
```

### SSL Certificate Issues
```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)

