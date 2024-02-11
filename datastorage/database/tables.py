import sqlalchemy

from datetime import datetime

from sqlalchemy import MetaData

from datastorage.database.classes import TableName

metadata = MetaData()


user = sqlalchemy.Table(
    TableName.USER,
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('first_name', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('second_name', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('email', sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column('hashed_password', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('is_active', sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column('is_superuser', sqlalchemy.Boolean),
    sqlalchemy.Column('is_verified', sqlalchemy.Boolean),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP, default=datetime.now),
)

community_settings = sqlalchemy.Table(
    TableName.COMMUNITY_SETTINGS,
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('user', sqlalchemy.String,
                      sqlalchemy.ForeignKey('user.id'), nullable=True, index=True),
    sqlalchemy.Column('community', sqlalchemy.String,
                      sqlalchemy.ForeignKey('community.id'), nullable=True, index=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('quorum', sqlalchemy.SmallInteger, nullable=False),
    sqlalchemy.Column('vote', sqlalchemy.SmallInteger, nullable=False),
)
#
community = sqlalchemy.Table(
    TableName.COMMUNITY,
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('main_settings', sqlalchemy.String,
                      sqlalchemy.ForeignKey('community_settings.id'), nullable=False, index=True),
    sqlalchemy.Column('creator', sqlalchemy.String,
                      sqlalchemy.ForeignKey('user.id'), nullable=False, index=True),
    sqlalchemy.Column('created', sqlalchemy.TIMESTAMP, default=datetime.now),
)

