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

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
PASSWORD_SECRET_KEY = os.environ.get('PASSWORD_SECRET_KEY')

HOST = str(os.environ.get('HOST', 'localhost'))
PORT = int(os.environ.get('PORT', '8080'))
