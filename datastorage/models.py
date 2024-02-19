from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, SmallInteger, Boolean
from sqlalchemy.orm import DeclarativeBase

from datastorage.database.classes import TableName
from datastorage.utils import build_uuid


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = TableName.USER

    id = Column(String, primary_key=True, default=build_uuid)
    firstname = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String, nullable=False)
    created = Column(TIMESTAMP, default=datetime.now)


class CommunitySettings(Base):
    __tablename__ = TableName.COMMUNITY_SETTINGS

    id = Column(String, primary_key=True, default=build_uuid)
    user = Column(String, ForeignKey(f'{TableName.USER}.id'), nullable=True, index=True)
    community = Column(String, ForeignKey('community.id'), nullable=True, index=True)
    name = Column(String, nullable=False)
    quorum = Column(SmallInteger, nullable=False)
    vote = Column(SmallInteger, nullable=False)


class Community(Base):
    __tablename__ = TableName.COMMUNITY

    id = Column(String, primary_key=True, default=build_uuid)
    main_settings = Column(String, ForeignKey(
        f'{TableName.COMMUNITY_SETTINGS}.id'), nullable=False, index=True)
    creator = Column(String, ForeignKey(f'{TableName.USER}.id'), nullable=False, index=True)
    created = Column(TIMESTAMP, default=datetime.now)
