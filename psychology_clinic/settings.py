"""
Django settings for psychology_clinic project.

Psychology Clinic Backend - Australian Configuration
Configured for Twilio Video, WhatsApp, Stripe, and Australian healthcare compliance.
"""

import os
from pathlib import Path
from datetime import timedelta

# Try to use python-decouple if available, otherwise use os.environ
try:
    from decouple import config  # type: ignore
except ImportError:
    # Fallback if decouple is not installed
    def config(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast and value is not None:
            if cast == bool:
                # Handle boolean conversion for strings
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
            return cast(value)
        return value

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-7g&jz)c!ge(y*h0&3o2tzcuwq9h58d%6bsn+475o*@syg3nh)z')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    'django_extensions',
    'django_celery_beat',
    'django_celery_results',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

LOCAL_APPS = [
    'core',
    'users',
    'services',
    'appointments',
    'billing',
    'resources',
    'audit',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Development apps
# Debug toolbar disabled to prevent profiling conflicts
# if DEBUG:
#     INSTALLED_APPS += [
#         'debug_toolbar',
#     ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'audit.middleware.AuditLoggingMiddleware',  # Audit logging middleware
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Development middleware
# Debug toolbar middleware disabled to prevent profiling conflicts
# if DEBUG:
#     MIDDLEWARE += [
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     ]

ROOT_URLCONF = 'psychology_clinic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'psychology_clinic.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Use DATABASE_URL for production, SQLite for development
DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    try:
        import dj_database_url  # type: ignore
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL)
        }
    except ImportError:
        # Fallback to SQLite if dj_database_url not available
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization - Australian Configuration
LANGUAGE_CODE = 'en-au'
TIME_ZONE = config('TIME_ZONE', default='Australia/Sydney')
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite React frontend
    "http://127.0.0.1:5173",
    "http://localhost:8080",  # Vue frontend
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings for development
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'access-control-allow-methods',
    'access-control-allow-headers',
    'access-control-allow-origin',
]

# CORS methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# CORS preflight settings
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Twilio Configuration
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_API_KEY = config('TWILIO_API_KEY', default='')
TWILIO_API_SECRET = config('TWILIO_API_SECRET', default='')
TWILIO_WHATSAPP_FROM = config('TWILIO_WHATSAPP_FROM', default='whatsapp:+14155238886')
# Optional: Status callback URL for video room events (webhooks)
# Set this to your public URL + /api/appointments/twilio-status-callback/
# For local development, use ngrok or similar: https://your-ngrok-url.ngrok.io/api/appointments/twilio-status-callback/
TWILIO_STATUS_CALLBACK_URL = config('TWILIO_STATUS_CALLBACK_URL', default='')

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Email Configuration (SendGrid via Twilio)
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')
SENDGRID_FROM_EMAIL = config('SENDGRID_FROM_EMAIL', default='noreply@yourclinic.com.au')
SENDGRID_FROM_NAME = config('SENDGRID_FROM_NAME', default='Psychology Clinic')

# Fallback to Django SMTP if SendGrid not configured
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Default from email
DEFAULT_FROM_EMAIL = SENDGRID_FROM_EMAIL or EMAIL_HOST_USER
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Django Allauth Configuration
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True

# Swagger/OpenAPI Configuration
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
}

# Australian Healthcare Specific Settings
MEDICARE_PROVIDER_NUMBER = config('MEDICARE_PROVIDER_NUMBER', default='')
AHPRA_REGISTRATION_NUMBER = config('AHPRA_REGISTRATION_NUMBER', default='')

# Privacy Policy Compliance (Privacy Act 1988)
PRIVACY_POLICY_VERSION = config('PRIVACY_POLICY_VERSION', default='1.0')
PRIVACY_POLICY_URL = config('PRIVACY_POLICY_URL', default='https://yourclinic.com.au/privacy-policy')
CONSENT_FORM_VERSION = config('CONSENT_FORM_VERSION', default='1.0')
TELEHEALTH_CONSENT_VERSION = config('TELEHEALTH_CONSENT_VERSION', default='1.0')
TELEHEALTH_RECORDING_CONSENT_VERSION = config('TELEHEALTH_RECORDING_CONSENT_VERSION', default='1.0')
TELEHEALTH_REQUIREMENTS_URL = config('TELEHEALTH_REQUIREMENTS_URL', default='https://yourclinic.com.au/telehealth-requirements')
PROGRESS_SHARING_CONSENT_VERSION = config('PROGRESS_SHARING_CONSENT_VERSION', default='1.0')

# Third-Party Data Sharing Disclosure (Privacy Act 1988 - APP 8)
# This documents all third-party services that receive patient data
THIRD_PARTY_DATA_SHARING = {
    'twilio': {
        'name': 'Twilio Inc.',
        'purpose': 'Video calls and SMS/WhatsApp notifications',
        'data_shared': ['name', 'phone_number', 'email_address'],
        'location': 'United States',
        'privacy_policy_url': 'https://www.twilio.com/legal/privacy',
        'safeguards': [
            'Encrypted transmission (TLS/SSL)',
            'GDPR compliant',
            'SOC 2 Type II certified',
            'Data processing agreements in place'
        ],
        'active': bool(TWILIO_ACCOUNT_SID),  # Only active if configured
    },
    'stripe': {
        'name': 'Stripe, Inc.',
        'purpose': 'Payment processing',
        'data_shared': ['name', 'email_address', 'payment_card_information'],
        'location': 'United States',
        'privacy_policy_url': 'https://stripe.com/au/privacy',
        'safeguards': [
            'PCI DSS Level 1 compliant',
            'Encrypted transmission (TLS/SSL)',
            'Tokenization of payment data',
            'No storage of full card numbers'
        ],
        'active': bool(STRIPE_SECRET_KEY),  # Only active if configured
    },
    'sendgrid': {
        'name': 'SendGrid (via Twilio)',
        'purpose': 'Email delivery for appointment reminders and notifications',
        'data_shared': ['email_address', 'name'],
        'location': 'United States',
        'privacy_policy_url': 'https://www.twilio.com/legal/privacy',
        'safeguards': [
            'Encrypted transmission (TLS/SSL)',
            'GDPR compliant',
            'Data processing agreements in place'
        ],
        'active': bool(SENDGRID_API_KEY),  # Only active if configured
    },
}

# Australian GST Rate (10%)
GST_RATE = 0.10

# Australian Phone Number Format
PHONE_NUMBER_DEFAULT_REGION = 'AU'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Development Settings
if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Debug Toolbar Configuration
    DEBUG_TOOLBAR_CONFIG = {
        'DISABLE_PANELS': [
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ],
        'SHOW_TEMPLATE_CONTEXT': True,
    }

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'psychology_clinic': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)