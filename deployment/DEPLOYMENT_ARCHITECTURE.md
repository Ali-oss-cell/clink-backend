# 🏗️ Backend Deployment Architecture Explained

## How Services Work Together

### Request Flow

```
Internet Request
    ↓
[Nginx] (Port 80/443)
    ↓ (Reverse Proxy)
[Gunicorn] (WSGI Server)
    ↓ (Python WSGI Protocol)
[Django Application] (Your Code)
    ↓ (Database Queries)
[PostgreSQL] (Database)
```

## Components Explained

### 1. **Nginx** (Web Server / Reverse Proxy)
**What it does:**
- Listens on ports 80 (HTTP) and 443 (HTTPS)
- Receives all incoming requests
- Serves static files directly (CSS, JS, images)
- Proxies dynamic requests to Gunicorn
- Handles SSL/TLS encryption
- Provides security headers

**Why we need it:**
- Fast static file serving
- SSL termination
- Security (firewall, rate limiting)
- Load balancing (if needed later)

### 2. **Gunicorn** (WSGI HTTP Server)
**What it does:**
- Runs your Django application
- Handles multiple worker processes
- Manages Python processes
- Communicates with Django via WSGI protocol

**Why we need it:**
- Django's development server (`runserver`) is NOT for production
- Gunicorn is production-ready
- Handles multiple concurrent requests
- Better performance and stability

### 3. **WSGI** (Web Server Gateway Interface)
**What it is:**
- A protocol/interface between web servers and Python applications
- Django's `wsgi.py` file implements this
- Gunicorn uses WSGI to communicate with Django

**Why we need it:**
- Standard way to run Python web apps
- Allows Nginx to talk to Django
- Industry standard for Python web applications

### 4. **Django Application**
**What it does:**
- Your actual application code
- Handles requests, business logic
- Connects to database
- Returns responses

### 5. **PostgreSQL** (Database)
**What it does:**
- Stores all your data
- Handles database queries
- Manages relationships between data

## Service Dependencies

```
Nginx → Gunicorn → Django → PostgreSQL
         ↓
      Celery → Redis → Background Tasks
```

## What You Need to Deploy

### Required Services:
1. ✅ **Nginx** - Web server (handles HTTP/HTTPS)
2. ✅ **Gunicorn** - WSGI server (runs Django)
3. ✅ **PostgreSQL** - Database (local or managed)
4. ✅ **Redis** - For Celery tasks
5. ✅ **Celery Worker** - Background tasks
6. ✅ **Celery Beat** - Scheduled tasks

### Optional Services:
- SSL Certificate (Let's Encrypt)
- Firewall (UFW)

## Configuration Files

### 1. `nginx.conf`
- **Location**: `/etc/nginx/sites-available/psychology_clinic`
- **Purpose**: Tells Nginx how to handle requests
- **Key settings**: 
  - Which domains/IPs to listen to
  - Where to proxy requests (Gunicorn socket)
  - Static file locations

### 2. `gunicorn.service`
- **Location**: `/etc/systemd/system/gunicorn.service`
- **Purpose**: Systemd service to run Gunicorn
- **Key settings**:
  - How many worker processes
  - Socket file location
  - Django application path

### 3. `celery.service` & `celery-beat.service`
- **Location**: `/etc/systemd/system/`
- **Purpose**: Run background tasks
- **Key settings**:
  - Redis connection
  - Task queue configuration

## How They Work Together

### Example Request Flow:

1. **User visits**: `http://209.38.89.74/api/users/`
2. **Nginx receives** the request on port 80
3. **Nginx checks** `nginx.conf`:
   - Matches `server_name 209.38.89.74`
   - Sees it's not a static file
   - Proxies to `unix:/var/www/clink-backend/gunicorn.sock`
4. **Gunicorn receives** the request via Unix socket
5. **Gunicorn calls** Django via WSGI (`psychology_clinic.wsgi:application`)
6. **Django processes** the request:
   - Routes to `/api/users/` endpoint
   - Queries PostgreSQL database
   - Returns JSON response
7. **Response flows back**: Django → Gunicorn → Nginx → User

## Socket Communication

Gunicorn and Nginx communicate via a **Unix socket file**:
- Location: `/var/www/clink-backend/gunicorn.sock`
- Faster than TCP/IP
- More secure (local only)
- No network overhead

## Static Files

Nginx serves static files directly (faster):
- CSS, JavaScript, images
- Location: `/var/www/clink-backend/staticfiles/`
- Collected by: `python manage.py collectstatic`

## Background Tasks

Celery handles:
- Email sending
- WhatsApp notifications
- Scheduled reminders
- Uses Redis as message broker

## Summary

**You need ALL of these:**
- ✅ Nginx (web server)
- ✅ Gunicorn (WSGI server)
- ✅ Django (your app)
- ✅ PostgreSQL (database)
- ✅ Redis (task queue)
- ✅ Celery Worker (background tasks)
- ✅ Celery Beat (scheduled tasks)

**They all work together** - you can't skip any of them for a production deployment!

