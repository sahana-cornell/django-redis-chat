import os

PG_NAME = os.getenv('POSTGRES_DB', 'chat')
PG_USER = os.getenv('POSTGRES_USER', 'chat')
PG_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'chat')
PG_HOST = os.getenv('POSTGRES_HOST', 'db')   # default stays 'db' for local docker
PG_PORT = os.getenv('POSTGRES_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': PG_NAME,
        'USER': PG_USER,
        'PASSWORD': PG_PASSWORD,
        'HOST': PG_HOST,
        'PORT': PG_PORT,
    }
}
