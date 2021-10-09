"""
Django settings for cass project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

if os.getenv("CI_CD_STAGE", None) is None:
    # Only loads in dev environment
    from dotenv import load_dotenv

    load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
CI_CD_STAGE = os.environ["CI_CD_STAGE"]

if CI_CD_STAGE == "production":
    DEBUG = False
elif CI_CD_STAGE == "testing" or CI_CD_STAGE == "development":
    DEBUG = True

ALLOWED_HOSTS = [os.environ["API_HOSTNAME"]]


# Application definition

INSTALLED_APPS = [
    "django_cassandra_engine",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "rest_framework_api_key",
    "knox",
    "channels",
    "authentication",
    "profiles",
    "socials",
    "chat",
    "notification",
    "analytics",
    "league_of_legends",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "rollbar.contrib.django.middleware.RollbarNotifierMiddleware",
]

ROOT_URLCONF = "proeliumx.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "proeliumx.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if CI_CD_STAGE == "development":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif CI_CD_STAGE == "testing":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ["DB_HOSTNAME"],
            "PORT": os.environ["DB_PORT"],
        },
        "chat": {
            "ENGINE": "django_cassandra_engine",
            "NAME": "db",
            "TEST_NAME": "test_db",
            "HOST": "localhost",
            "OPTIONS": {
                "replication": {
                    "strategy_class": "SimpleStrategy",
                    "replication_factor": 1,
                }
            },
        },
    }
elif CI_CD_STAGE == "production":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["RDS_DB_NAME"],
            "USER": os.environ["RDS_USERNAME"],
            "PASSWORD": os.environ["RDS_PASSWORD"],
            "HOST": os.environ["RDS_HOSTNAME"],
            "PORT": os.environ["RDS_PORT"],
        },
        "chat": {
            "ENGINE": "django_cassandra_engine",
            "NAME": "db",
            "TEST_NAME": "test_db",
            "HOST": "localhost",
            "OPTIONS": {
                "replication": {
                    "strategy_class": "SimpleStrategy",
                    "replication_factor": 1,
                }
            },
        },
    }

DATABASE_ROUTERS = ["chat.db_router.ChatRouter"]

REDIS_URL = "redis://{}:{}@{}:{}".format(
    os.environ["REDIS_USERNAME"],
    os.environ["REDIS_PASSWORD"],
    os.environ["REDIS_HOSTNAME"],
    os.environ["REDIS_PORT"],
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


################################################################################
AUTH_USER_MODEL = "authentication.User"


################################################################################
# CORS
CORS_ALLOW_ALL_ORIGINS = True


################################################################################
# API Key
API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-api-key",
]


################################################################################
# Knox
from datetime import timedelta

REST_KNOX = {
    "TOKEN_TTL": timedelta(days=30),
    "AUTO_REFRESH": True,
}


################################################################################
# Chat
ASGI_APPLICATION = "proeliumx.routing.application"
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
#     }
# }


################################################################################

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"


################################################################################
# Rollbar
ROLLBAR = {
    "access_token": os.environ["ROLLBAR_ACCESS_TOKEN"],
    "environment": "development" if DEBUG else "production",
    "root": BASE_DIR,
}
import rollbar

rollbar.init(**ROLLBAR)

################################################################################
# Only transmit HTTPS requests to Django
# if CI_CD_STAGE == "production":
#     CSRF_COOKIE_SECURE = True
#     SESSION_COOKIE_SECURE = True
