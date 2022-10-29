import os


DATABASE_CONNECTION_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
    os.environ.get('DB_USER', 'postgres'),
    os.environ.get('DB_PASSWORD', '1234'),
    os.environ.get('DB_HOST', 'localhost'),
    os.environ.get('DB_PORT', '5432'),
    os.environ.get('DB_NAME', 'self-org'),
)

HOST = str(os.environ.get('HOST', 'localhost'))
PORT = int(os.environ.get('PORT', '8080'))
