"""
Django settings for serverConfig project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^#5m^owy^$jnqt6ac=!lyqnsrq3lm)a^2yxf+h6n_^)xs@s*@f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [".vercel.app", "127.0.0.1", "localhost"]


# Installed Apps

DJANGO_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

PROJECT_APPS = [
    "accounts",
    "api",
    "admin_panel"
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "drf_yasg",
    "djoser",
    "corsheaders",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware", # middleware for cors-headers
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTH_USER_MODEL = "accounts.User"

ROOT_URLCONF = 'serverConfig.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'serverConfig.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DATABASE'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),  # Remote host
        'OPTIONS': {
            'sslmode': 'require',  # Required for Supabase
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# EMAIL CONFIG
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "urkelcodes7@gmail.com"
EMAIL_HOST_PASSWORD = "xkcj ugeb ypbw dlww"
EMAIL_USE_TLS = True


REST_FRAMEWORK = {
  'DEFAULT_AUTHENTICATION_CLASSES': (
      'serverConfig.authenticate.CustomAuthentication',
  ),
}


from datetime import timedelta
SIMPLE_JWT = {
  'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
  'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
  'ROTATE_REFRESH_TOKENS': False,
  'BLACKLIST_AFTER_ROTATION': True,
  'UPDATE_LAST_LOGIN': False,

  'ALGORITHM': 'HS256',
  'SIGNING_KEY': SECRET_KEY,
  'VERIFYING_KEY': None,
  'AUDIENCE': None,
  'ISSUER': None,

  'AUTH_HEADER_TYPES': ('Bearer',),
  'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
  'USER_ID_FIELD': 'id',
  'USER_ID_CLAIM': 'user_id',
  'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

  'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
  "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
  'TOKEN_TYPE_CLAIM': 'token_type',

  'JTI_CLAIM': 'jti',

  'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
  'SLIDING_TOKEN_LIFETIME': timedelta(minutes=1),
  'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(minutes=2),

  # custom
  'AUTH_COOKIE': 'access_token',  # Cookie name. Enables cookies if value is set.
  'AUTH_COOKIE_DOMAIN': None,     # A string like "example.com", or None for standard domain cookie.
  'AUTH_COOKIE_SECURE': True,    # Whether the auth cookies should be secure (https:// only).
  'AUTH_COOKIE_HTTP_ONLY' : True, # Http only cookie flag.It's not fetch by javascript.
  'AUTH_COOKIE_PATH': '/',        # The path of the auth cookie.
  'AUTH_COOKIE_SAMESITE': 'None',  # Whether to set the flag restricting cookie leaks on cross-site requests. This can be 'Lax', 'Strict', or None to disable the flag.
}

# DJOSER CONFIG
DJOSER = {
    "LOGIN_FIELD": "username",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "SEND_CONFIRMATION_EMAIL": False,
    "SET_USERNAME_RETYPE": True,
    "SET_PASSWORD_RETYPE": True,
    "USERNAME_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}",
    "PASSWORD_RESET_CONFIRM_URL": "email/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": False,
    "SOCIAL_AUTH_TOKEN_STRATEGY": "djoser.social.token.jwt.TokenStrategy",
    "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": [
        "your redirect url",
        "your redirect url",
    ],
    
    "SERIALIZERS": {
        "user_create": "accounts.serializers.UserCreateSerializer",
        "user": "accounts.serializers.UserSerializer",
        "current_user": "accounts.serializers.UserSerializer",
        "user_delete": "accounts.serializers.UserSerializer",
    },
}



CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://klikk-up.vercel.app",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://klikk-up.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True  

CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
