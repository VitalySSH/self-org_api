import os

from dotenv import load_dotenv


load_dotenv()

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')

DATABASE_CONNECTION_STR = 'postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
)

PRODUCTION_MODE = (os.environ.get('PRODUCTION_MODE', '')).lower() == 'true' or False

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
PASSWORD_SECRET_KEY = os.environ.get('PASSWORD_SECRET_KEY')
JWT_LIFE_TIME_SECONDS = int(os.environ.get('JWT_LIFE_TIME_SECONDS'))
COOKIE_TOKEN_NAME = os.environ.get('COOKIE_TOKEN_NAME')

HOST = str(os.environ.get('HOST', 'localhost'))
PORT = int(os.environ.get('PORT', '8080'))

UPLOADED_FILES_PATH = 'filestorage/uploaded_files/'
