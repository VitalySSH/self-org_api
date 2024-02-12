from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, SmallInteger

from datastorage.classes import Base
from datastorage.database.classes import TableName
from datastorage.utils import build_uuid


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