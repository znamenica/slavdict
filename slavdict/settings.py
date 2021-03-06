# -*- coding: UTF-8 -*-
"""
Django settings for slavdict project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from os import environ
from os.path import (abspath, dirname, normpath)
import sys
import importlib
import __builtin__

def apply_globals(m):
    for item in dir(m):
        if not item.startswith("__"):
            globals()[item] = eval( "m.%s" % item )

# Базовые настройки проекта,
# от которых могут зависеть другие настройки
ROOT = normpath(abspath(dirname(dirname(__file__)))).replace('\\', '/') + '/'
__builtin__.DJANGO_ROOT = ROOT

# Настройки, зависящие от базовых
# либо от которых не зависят другие настройки.

ADMINS = ()
MANAGERS = ADMINS
BACKUP_MANAGERS = MANAGERS
BACKUP_DIR = ROOT + '.dumps/'

INTERNAL_IPS = ('127.0.0.1',)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'
USE_TZ = False

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

USE_I18N = True
USE_L10N = True

# URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ROOT + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/u/'

STATIC_ROOT = ROOT + '.static/'
STATIC_URL = '/static/'
STATIC_RESOURCES_VERSION='2015.06.29'
CSS_PATH = STATIC_URL + 'css/'
JS_PATH = STATIC_URL + 'js/'
IMAGE_PATH = STATIC_URL

# Make this unique, and don't share it with anybody.
SECRET_KEY = environ['SLAVDICT_SECRET_KEY']

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

#from jinja2 import StrictUndefined
JINJA2_ENVIRONMENT_OPTIONS = {
    'autoescape': False,
#    'undefined': StrictUndefined,
}

JINJA2_EXTENSIONS = (
    'slavdict.django_template_spaces.templatetags.trim_spaces.trim',
)

MIDDLEWARE_CLASSES = (
    'slavdict.middleware.CookieVersionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
   #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'coffin',
    'djcompass',

    'slavdict.dictionary',
    'slavdict.custom_user',
    'slavdict.django_template_spaces',
]

ROOT_URLCONF = 'slavdict.urls'

WSGI_APPLICATION = 'slavdict.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOT + 'templates/',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'slavdict.context_processors.staticfiles',
)

STATICFILES_DIRS = (
    ROOT + 'static/',
)

ALLOWED_HOSTS= [ '*' ]

######################################
##  Настройки отдельных приложений  ##
######################################

#compass
COMPASS_INPUT = ROOT + 'sass'
COMPASS_OUTPUT = ROOT + 'static/css'
COMPASS_IMAGE_DIR = ROOT + IMAGE_PATH
COMPASS_SCRIPT_DIR = ROOT + JS_PATH
COMPASS_STYLE = 'compact'


# custom_user
AUTHENTICATION_BACKENDS = (
    'slavdict.auth_backends.CustomUserModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)
CUSTOM_USER_MODEL = 'slavdict.custom_user.CustomUser'


# Сторонние библиотеки JavaScript
JSLIBS_VERSION = '2014.10.31'
JSLIBS_URL = STATIC_URL + 'js/outsourcing/'
JSLIBS_PATH = ROOT + 'static/js/outsourcing/'
JSLIBS_LOCAL = ()


# до и переопределение настроек проекта для выбранного окружения:
# {development, production, test }
ENV = environ.get( 'SLAVDICT_ENVIRONMENT', 'development' )
if ENV not in ( 'development', 'production', 'test' ):
    raise ValueError( "Invalid environment %s specified" % ENV )

# импортирование переменных из подмодуля окружения
m = __import__( '%s_settings' % ENV, globals={"__name__": __name__} )
apply_globals(m)

try:
    INSTALLED_APPS.extend( INSTALLED_APPS_EXTENSION )
except NameError:
    pass

# NOTE: Файлы с raw.githubusercontent.com нельзя отдавать в продакшн.
# Там выставляются http-заголовки
#
#   Content-Type: text/plain; charset=utf-8
#   X-Content-Type-Options: nosniff
#
# что запрещает браузеру распознавать js-файл как js-файл.
# Домен rawgit.com специально предназначен в помощь разработчикам для
# обхода этой проблемы, но расчитан исключительно для тестирования,
# отладки, демонстрации. При нагрузке его трафиком соединения будут
# скидываться. См. http://rawgit.com/
#
# Переменная JSLIBS_LOCAL говорит о том, пути к каким файлам подменять на локальные# чтобы именно они использовались в боевом окружении.
JSLIBS = {}
for lib in JSLIBS_LOCAL:
    filename = JSLIBS_SOURCE[lib].split('/')[-1].split('?')[0]
    JSLIBS[lib] = JSLIBS_URL + filename + '?' + STATIC_RESOURCES_VERSION

for lib in [x for x in JSLIBS_SOURCE.keys() if x not in JSLIBS_LOCAL]:
    JSLIBS[lib] = JSLIBS_SOURCE[lib]

# When using Auto Escape you will notice that marking something as
# a Safestrings with Django will not affect the rendering in Jinja 2. To fix
# this you can monkeypatch Django to produce Jinja 2 compatible Safestrings:
from django.utils import safestring
if not hasattr(safestring, '__html__'):
    safestring.SafeString.__html__ = lambda self: str(self)
    safestring.SafeUnicode.__html__ = lambda self: unicode(self)


