from .base import *  # noqa
import os
import dj_database_url
import sentry_sdk

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = [os.environ["DOMAIN"]]
CSRF_TRUSTED_ORIGINS = [f"https://{os.environ['DOMAIN']}"]

SECRET_KEY = os.environ["RANDOM_SECRET_KEY"]


# Built-in email sending service provided by CodeRed Cloud.
# Change this to a different backend or SMTP server to use your own.
EMAIL_BACKEND = "django_sendmail_backend.backends.EmailBackend"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config(conn_max_age=500)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

WAGTAILADMIN_BASE_URL = f"http://{os.environ['VIRTUAL_HOST']}"

sentry_sdk.init(
    dsn="https://bb7228c88b0dac77326a2caec3313469@o155705.ingest.us.sentry.io/4509176694833152",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)