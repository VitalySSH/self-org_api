from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, String, ForeignKey, SmallInteger, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase

from datastorage.database.classes import TableName
from datastorage.utils import build_uuid


class Base(DeclarativeBase):
    pass


class SQLAlchemyBaseUserTableId(SQLAlchemyBaseUserTable[str]):
    id = Column(String, primary_key=True, default=build_uuid)


class User(SQLAlchemyBaseUserTableId, Base):
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    created = Column(TIMESTAMP, default=datetime.now)


class CommunitySettings(Base):
    __tablename__ = TableName.COMMUNITY_SETTINGS

    id = Column(String, primary_key=True, default=build_uuid)
    user = Column(String, ForeignKey('user.id'), nullable=True, index=True)
    community = Column(String, ForeignKey('community.id'), nullable=True, index=True)
    name = Column(String, nullable=False)
    quorum = Column(SmallInteger, nullable=False)
    vote = Column(SmallInteger, nullable=False)


class Community(Base):
    __tablename__ = TableName.COMMUNITY

    id = Column(String, primary_key=True, default=build_uuid)
    main_settings = Column(String, ForeignKey('community_settings.id'), nullable=False, index=True)
    creator = Column(String, ForeignKey('user.id'), nullable=False, index=True)
    created = Column(TIMESTAMP, default=datetime.now)
