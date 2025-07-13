import os

from dotenv import load_dotenv


load_dotenv()

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

DATABASE_CONNECTION_STR = 'postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
)

PRODUCTION_MODE = (os.environ.get('PRODUCTION_MODE', '')).lower() == 'true' or False

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
PASSWORD_SECRET_KEY = os.environ.get('PASSWORD_SECRET_KEY')
JWT_LIFE_TIME_SECONDS = int(os.environ.get('JWT_LIFE_TIME_SECONDS'))
COOKIE_TOKEN_NAME = os.environ.get('COOKIE_TOKEN_NAME')

HOST = str(os.environ.get('HOST', 'localhost'))
PORT = int(os.environ.get('PORT', '8080'))

UPLOADED_FILES_PATH = 'filestorage/uploaded_files/'
