from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ijlk1srzd4jeeg^^9q)dj(9h)+86g@qrbr#*aj*+-1$upobi89"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CACHES = {
    "default": {
        # "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": os.path.join(BASE_DIR, ".cache"),
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ["DB_HOST"],
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "OPTIONS": {
            "client_encoding": "UTF8",
        },
    }
}

try:
    from .local import *
except ImportError:
    pass
