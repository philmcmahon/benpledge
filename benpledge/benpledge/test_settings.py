import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }
}

SOUTH_TESTS_MIGRATE = False

PASSWORD_HASHERS = (
'django.contrib.auth.hashers.SHA1PasswordHasher',
'django.contrib.auth.hashers.PBKDF2PasswordHasher',
'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
'django.contrib.auth.hashers.BCryptPasswordHasher',
'django.contrib.auth.hashers.MD5PasswordHasher',
'django.contrib.auth.hashers.CryptPasswordHasher',
)