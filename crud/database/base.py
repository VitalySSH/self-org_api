from databases import Database
from sqlalchemy import create_engine

from core.config import DATABASE_CONNECTION_STR

database = Database(DATABASE_CONNECTION_STR)
engine = create_engine(DATABASE_CONNECTION_STR)
