import dj_database_url

from datetime import timedelta
from decouple import config
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1, localhost",
    cast=lambda v: [s.strip() for s in v.split(",")],
)


# Application definition

INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "djoser",
    "drf_spectacular",
    # Local apps
    "apps.core",
    "apps.users",
    "apps.restaurant",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database

DATABASE_URL = config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=DATABASE_URL.startswith(("postgres://", "postgresql://")),
    )
}


# Password validation

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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

if not DEBUG:
    STATIC_ROOT = BASE_DIR / "staticfiles"

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework Settings

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        # Baseline protection for everyone
        "anon": "60/min",
        "user": "300/min",
        # Auth rates
        "auth_login": "10/min",
        "auth_me": "60/min",
        "auth_refresh": "30/min",
        "auth_verify": "60/min",
        "auth_logout": "10/min",
        "demo_create": "3/hour",
        # Menu rates
        "menuitems_read": "180/min",
        "menuitems_write": "30/min",
        "categories_read": "120/min",
        "categories_write": "20/min",
        # Cart rates
        "cart_read": "120/min",
        "cart_write": "60/min",
        "cart_clear": "10/min",
        # Order rates
        "orders_read": "120/min",
        "orders_create": "10/min",
        "orders_update": "30/min",
        "orders_delete": "10/min",
        # Group rates
        "groups_read": "60/min",
        "groups_write": "10/min",
        "groups_deliverycrew_remove": "5/min",
        # customer list
        "customers_read": "30/min",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Only enable the Browsable API in development
if DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
        "rest_framework.renderers.BrowsableAPIRenderer",
    )

# JWT / Auth

AUTH_USER_MODEL = "users.CustomUser"

ACCESS_TOKEN_LIFETIME_MINUTES = config(
    "ACCESS_TOKEN_LIFETIME_MINUTES", cast=int, default=30
)
REFRESH_TOKEN_LIFETIME_HOURS = config(
    "REFRESH_TOKEN_LIFETIME_HOURS", cast=int, default=168  # 7 days
)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=REFRESH_TOKEN_LIFETIME_HOURS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "LEEWAY": 30,
    "USER_ID_FIELD": "uuid",
    "USER_ID_CLAIM": "user_uuid",
}

DJOSER = {
    "TOKEN_MODEL": None,  # Disable authtoken model when using JWT
    "SERIALIZERS": {
        "user_create": "djoser.serializers.UserCreateSerializer",
        "user": "djoser.serializers.UserSerializer",
    },
}

# Expose Djoser user endpoints (useful for development and debugging)
EXPOSE_DJOSER = config("EXPOSE_DJOSER", cast=bool, default=False)

LOGIN_REDIRECT_URL = "/api/v1/auth/users/me"

# Demo Mode Settings

DEMO_MODE = config("DEMO_MODE", cast=bool, default=False)
DEMO_USER_TTL_HOURS = config("DEMO_USER_TTL_HOURS", cast=int, default=12)

# drf-spectacular Settings

# Build authentication-related OpenAPI tags dynamically based on DEBUG and DEMO_MODE
AUTH_TAGS = []
if DEBUG or not DEMO_MODE:
    # In development (DEBUG=True) or when demo mode is disabled (DEMO_MODE=False),
    # expose the standard Authentication tag.
    AUTH_TAGS = [
        {
            "name": "Authentication",
            "description": (
                "Endpoints for authenticating users and managing JSON Web Tokens (JWTs)."
            ),
        }
    ]
if DEMO_MODE:
    # In demo mode, also expose the Demo Authentication tag.
    AUTH_TAGS += [
        {
            "name": "Demo Authentication",
            "description": (
                "Endpoints for creating and managing temporary demo users and their "
                "authentication tokens."
            ),
        }
    ]

SPECTACULAR_SETTINGS = {
    "SERVE_INCLUDE_SCHEMA": False,  # hide schema from /docs UI
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,  # keep JWT token when refreshing the page
    },
    "COMPONENT_SPLIT_REQUEST": True,
    # Keep endpoints ordered how they appear in the project
    "SORT_OPERATIONS": False,
    "SORT_OPERATION_PARAMETERS": False,
    # General schema metadata
    "TITLE": "Restaurant API",
    "DESCRIPTION": "A REST API for managing restaurant menus, orders, and role-based user access.",
    "VERSION": "1.0.0",
    "TAGS": [
        *AUTH_TAGS,
        {
            "name": "Categories",
            "description": (
                "Endpoints for creating, retrieving, updating, and deleting menu categories."
            ),
        },
        {
            "name": "Menu",
            "description": (
                "Endpoints for creating, retrieving, updating, and deleting menu items."
            ),
        },
        {
            "name": "Cart",
            "description": (
                "Endpoints for creating, retrieving, updating, and deleting items in "
                "the customer's cart."
            ),
        },
        {
            "name": "Orders",
            "description": (
                "Endpoints for creating, retrieving, updating, and deleting "
                "customer orders based on user role."
            ),
        },
        {
            "name": "Role Groups",
            "description": (
                "Endpoints for managing manager, delivery crew, and customer "
                "role memberships."
            ),
        },
    ],
}
