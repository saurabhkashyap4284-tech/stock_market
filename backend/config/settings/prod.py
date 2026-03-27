from .base import *
import os
import dj_database_url

DEBUG = False

SECRET_KEY = os.getenv("SECRET_KEY", "prod-secret-key-change-this")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com").split(",")

# ── Database (PostgreSQL) ─────────────────────────────────────────
if os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE":   "django.db.backends.postgresql",
            "NAME":     os.getenv("DB_NAME", "fo_monitor"),
            "USER":     os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", "yourpassword"),
            "HOST":     os.getenv("DB_HOST", "db"),
            "PORT":     os.getenv("DB_PORT", "5432"),
        }
    }

# Ensure Redis is read from REDIS_URL if available
if os.getenv("REDIS_URL"):
    # Standard format: redis://red-xxxxx:6379
    REDIS_URL = os.getenv("REDIS_URL")
    # For Channels, we need a list of hosts
    # Note: Render Redis sometimes uses rediss:// (SSL)
    CHANNEL_LAYERS["default"]["CONFIG"]["hosts"] = [REDIS_URL]
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

# ── Security ──────────────────────────────────────────────────────
SECURE_SSL_REDIRECT     = os.getenv("SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE   = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
CSRF_COOKIE_SECURE      = os.getenv("CSRF_COOKIE_SECURE", "False") == "True"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── Static Files ──────────────────────────────────────────────────
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ── CORS ──────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
if not CORS_ALLOWED_ORIGINS[0]:
    CORS_ALLOWED_ORIGINS = []
