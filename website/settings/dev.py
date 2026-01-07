from .base import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ijlk1srzd4jeeg^^9q)dj(9h)+86g@qrbr#*aj*+-1$upobi89"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS=[
    "http://localhost:8000",
    "https://*.aldryn.io"
    ]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CACHES = {
    "default": {
        # "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": os.path.join(BASE_DIR, ".cache"),
    },
}

if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config(conn_max_age=500)}
elif "DEFAULT_DATABASE_HOSTNAME" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.environ.get("DEFAULT_DATABASE_HOSTNAME"),
            "NAME": os.environ.get("DEFAULT_DATABASE_DATABASE_NAME"),
            "USER": os.environ.get("DEFAULT_DATABASE_USERNAME"),
            "PASSWORD": os.environ.get("DEFAULT_DATABASE_PASSWORD"),
            "OPTIONS": {
                "client_encoding": "UTF8",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

try:
    from .local import *
except ImportError:
    pass
