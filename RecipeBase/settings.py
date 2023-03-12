"""
Django settings for RecipeBase project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from os import getenv
from pathlib import Path
import sys
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def getenv_list(name: str, default: str = "") -> list[str]:
    return list(filter(lambda s: s, os.getenv(name, default).split(",")))


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-)@)dls40j3tc#(m-pbg^&hhnr9zmz0)*7l)q#&n1ec8qz4c7gu",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG", False)
DEBUGBAR = getenv("DEBUGBAR", False)
TESTING = "pytest" in sys.modules

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS", "*").split(" ")

USE_X_FORWARDED_HOST = True
HOSTNAME_OVERRIDE = getenv("HOSTNAME_OVERRIDE", None)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3-party
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "ckeditor",
    "django_cleanup.apps.CleanupConfig",
    "adminsortable",
    "thumbnails",
    "multiselectfield",
    "django_q",
    "simple_history",
    # Custom
    "users.apps.UsersConfig",
    "recipes.apps.RecipesConfig",
    "tasks.apps.TasksConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "RecipeBase.urls"

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

WSGI_APPLICATION = "RecipeBase.wsgi.application"

INTERNAL_IPS = ["127.0.0.1", *os.getenv("INTERNAL_IPS", "").split(",")]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    *getenv_list("TRUSTED_ORIGINS"),
]

if TESTING:
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if os.environ.get("USE_DB_ENGINE") or os.environ.get("DB_ENGINE"):
    CONN_MAX_AGE = 100
    DATABASES: dict[str, Any] = {
        "default": {
            "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
            "NAME": os.environ.get("DB_NAME", "db.sqlite"),
            "USER": os.environ.get("DB_USER", ""),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", None),
            "PORT": os.environ.get("DB_PORT", None),
            "CONN_MAX_AGE": 600,
        }
    }
else:
    CONN_MAX_AGE = 5
    DATABASES: dict[str, Any] = {  # type: ignore
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
            "OPTIONS": {
                "timeout": 20,
            },
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    # },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    # {
    #     "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    # },
    # {
    #     "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    # },
]


AUTHENTICATION_BACKENDS = ["users.backends.CustomAuthorizationBackend"]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "ru"
LANGUAGES = [
    ("ru", "Русский"),
    # ('en', 'Английский'),
]

TIME_ZONE = "Asia/Famagusta"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / ".static_all"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CKEDITOR_UPLOAD_PATH = "uploads/ckeditor/"

if DEBUGBAR:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "users.backends.toolbar_callback",
}

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Cut", "Copy", "Paste", "PasteText", "-", "Undo", "Redo"],
            ["Bold", "Italic", "Underline", "Strike", "Format"],
            [
                "NumberedList",
                "BulletedList",
                "-",
                "Outdent",
                "Indent",
                "-",
                "JustifyLeft",
                "JustifyCenter",
                "JustifyRight",
                "JustifyBlock",
            ],
            ["Image", "Table"],
            ["Link", "Unlink"],
            ["RemoveFormat", "Source", "Maximize", "Preview"],
        ],
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.backends.CustomTokenAuthentication",
        # "rest_framework.authentication.TokenAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
        "users.backends.CsrfExemptSessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # "rest_framework.permissions.IsAuthenticated",
        # "rest_framework.permissions.DjangoModelPermissions"
        "users.backends.CustomModelPermissions",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "users.backends.TotalPagesPageNumberPagination",
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Recipe Base API",
    "DESCRIPTION": "Home base of recipes",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1",
    # 'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
}

THUMBNAILS = {
    "METADATA": {
        "BACKEND": "RecipeBase.thumbnails_backend.ThumbnailDBBackend",
    },
    "STORAGE": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "SIZES": {
        "small": {
            "PROCESSORS": [
                {
                    "PATH": "thumbnails.processors.resize",
                    "width": 200,
                    "height": 200,
                    "method": "fill",
                },
            ],
        },
    },
}

Q_CLUSTER = {
    # 'name': "recipebase",
    "label": "Recipe Base",
    "workers": 1,
    "recycle": 500,
    "timeout": 60,
    "retry": 120,
    "save_limit": 250,
    "queue_limit": 20,
    "orm": "default",
    "max_attempts": 10,
    # 'cpu_affinity': 1,
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module}.{funcName} {process:d} {thread:d} {message}",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "mail_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "level": "ERROR",
            "include_html": True,
        },
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        # "logfile": {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "level": "DEBUG",
        #     "filename": os.path.join(BASE_DIR, "django.log"),
        #     "maxBytes": 1024 * 30,  # in kb
        #     "backupCount": 1 if DEBUG else 5,
        #     "formatter": "verbose",
        # },
    },
    "loggers": {
        "": {"level": "DEBUG", "handlers": ["console"]},
        # "django.db.backends": {
        #     "level": "DEBUG",
        #     "handlers": ["console"],
        # },
    },
}
