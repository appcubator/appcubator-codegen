import os
import os.path

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(os.path.dirname(__file__), '..', 'collected_static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'slo51mrh=b57df_9(z$1o0rpl&amp;qo-xt%d_msh50k3k1t7$o$7@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'analytics.middleware.VisitorAnalyticsMiddleware', # Must be under AuthenticationMiddleware
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'webapp.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grappelli', # Must be be above django.contrib.admin!
    'django.contrib.admin',
    'social_auth', # django-social-auth
    'webapp',
    'south',
    'analytics',
    'import_export',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

AUTHENTICATION_BACKENDS = (
    'webapp.utils.EmailOrUsernameModelBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "social_auth.context_processors.social_auth_backends",
)

AUTH_USER_MODEL = "webapp.User"
# IMPORTANT: Allows for the case the user cancels. Enable during debugging.
SOCIAL_AUTH_RAISE_EXCEPTIONS = False


SOCIAL_AUTH_BACKEND_ERROR_URL = '/'
LOGIN_ERROR_URL = '/'
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

FACEBOOK_SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/__facebook_social_auth_callback/'
TWITTER_SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/__twitter_social_auth_callback/'
LINKEDIN_SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/__linkedin_social_auth_callback/'

FACEBOOK_APP_ID = '145000778994158'
FACEBOOK_API_SECRET = 'f5f3f2a69011b36da2005fbea8aa3476'
TWITTER_CONSUMER_KEY         = '4XzJvQ1nZTMVcVmPwBjw'
TWITTER_CONSUMER_SECRET      = 'YejAm6MhKfwh2YhqcG4Ljf0Hakgsnp5HzfyBA7bJBDk'
LINKEDIN_CONSUMER_KEY        = 't0q97cjtk5kf'
LINKEDIN_CONSUMER_SECRET     = '1R8SdQPxL9rzAlvD'

FACEBOOK_EXTENDED_PERMISSIONS = ['email']
LINKEDIN_SCOPE = ['r_basicprofile', 'r_emailaddress']
GRAPPELLI_ADMIN_TITLE = "Appcubator Admin"
