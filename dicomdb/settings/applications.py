INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_user_agents',
    'dicomdb.apps.base',
    'dicomdb.apps.main',
    'dicomdb.apps.watcher',
    'dicomdb.apps.api',
    'dicomdb.apps.users',
]

THIRD_PARTY_APPS = [
    'social_django',
    'crispy_forms',
    'opbeat.contrib.django',
    'djcelery',
    'django_cleanup',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'guardian',
    'django_gravatar',
    'lockdown',
    'taggit',
]


INSTALLED_APPS += THIRD_PARTY_APPS
