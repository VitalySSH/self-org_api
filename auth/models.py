from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, String, TIMESTAMP

from datastorage.classes import Base
from datastorage.utils import build_uuid


class SQLAlchemyBaseUserTableId(SQLAlchemyBaseUserTable[str]):
    id = Column(String, primary_key=True, default=build_uuid)


class User(SQLAlchemyBaseUserTableId, Base):
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    created = Column(TIMESTAMP, default=datetime.now)
