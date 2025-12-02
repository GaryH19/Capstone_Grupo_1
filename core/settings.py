import os
import sys
from decouple import config
from unipath import Path
import oracledb
from boto3.s3.transfer import TransferConfig


# INICIALIZACIÓN DEL CLIENTE ORACLE
try:
    oracledb.version = "8.3.0"
    sys.modules["cx_Oracle"] = oracledb
    print("Oracle Client: Modo compatibilidad cx_Oracle activado.")
except Exception as e:
    print(f"Error activando compatibilidad Oracle: {e}")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# --- 2. HOSTS PERMITIDOS ---
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    config('SERVER', default='*'),
    'boilerplate-code-django-dashboard.appseed.us',
    '144.22.46.224',
    '.ngrok-free.dev', 
    '.ngrok-free.app', 
    '.ngrok.io',
    '*' 
]

CSRF_TRUSTED_ORIGINS = [
    f"http://{config('SERVER', default='127.0.0.1')}",
    f"https://{config('SERVER', default='127.0.0.1')}",
    'http://144.22.46.224', 
    'https://144.22.46.224'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.home',
    'storages', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.NoCacheMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database OCI
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.sa-santiago-1.oraclecloud.com))(connect_data=(service_name=g5a1da9fefb2b93_docuflow_medium.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))',
        'USER': 'ADMIN',
        'PASSWORD': 'DocuFlow12345.',
    }
}
# Database local SQLite (descomentar para uso local)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         # Usamos os.path.join en lugar de la barra '/'
#         'NAME': os.path.join(BASE_DIR,'..', 'db.sqlite3'),
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_URL ='/media/'
MEDIA_ROOT = os.path.join(CORE_DIR, 'media')

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(CORE_DIR, 'apps/static'),
                    )

#############################################################
#############################################################

#Credenciales AWS S3 para almacenamiento de medios
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
# AWS_S3_SIGNATURE_NAME = 's3v4'
# AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL = None
# AWS_S3_VERIFY = True 
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# settings.py

# Credenciales de Oracle Cloud BUCKET para almacenamiento de medios
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
AWS_S3_SIGNATURE_NAME = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True 
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'






# Control de contraseñas en entorno de desarrollo
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = False
# DEFAULT_FROM_EMAIL = 'Soporte DocuFlow <soporte@docuflow.cl>'


# --- CONFIGURACIÓN DE CORREO (GMAIL) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Tu dirección de correo real (quien envía el mensaje)
EMAIL_HOST_USER = 'garyhernandezblanco19@gmail.com' 

# La "Contraseña de Aplicación" de 16 letras (NO tu clave normal)
EMAIL_HOST_PASSWORD = 'llsh ucvs uvet oayy' 

# El remitente que verán los usuarios
DEFAULT_FROM_EMAIL = 'Soporte DocuFlow garyhernandezblanco19@gmail.com'