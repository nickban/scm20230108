import os
from decouple import config
from django.contrib.messages import constants as messages

import mimetypes
mimetypes.add_type("text/css", ".css", True)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

DEBUG = True

if DEBUG:
    ALLOWED_HOSTS = ['127.0.0.1']
else:
    ALLOWED_HOSTS = ['47.97.208.188']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scm',
    'crispy_forms',
    'widget_tweaks',
    'tempus_dominus',  # 日期选择器
    'rest_framework',
]

TEMPUS_DOMINUS_LOCALIZE = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'templates/post/'),
                 os.path.join(BASE_DIR, 'templates/sample/'),
                 os.path.join(BASE_DIR, 'templates/order/'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
            'custom_tags':'scm.templatetags.custom_tags'
            }
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
}


AUTH_PASSWORD_VALIDATORS = []

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# 静态文件设置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 用户登录授权模块
AUTH_USER_MODEL = 'scm.User'

# @loginrequired装饰器返回地址, 没有登录就返回到登录页面, 因为是后台系统，强制登录系统, 否则无法访问
LOGIN_URL = 'login'

# 登录成功后,如果没有next,系统重定向到主页
LOGIN_REDIRECT_URL = 'home'

# 登出后重定向到登录页面
LOGOUT_REDIRECT_URL = 'login'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# 用户消息类型到CSS样式的映射
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

FILTERS_EMPTY_CHOICE_LABEL = '请选择'



EMAIL_BACKEND = config('EMAIL_BACKEND')
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
DEFAULT_FROM_EMAIL = '缘色SCM <SCM@monayoung.com.au>'
EMAIL_SUBJECT_PREFIX = '[缘色SCM] '
SERVER_EMAIL = 'SCM@monayoung.com.au'
