import sqlalchemy

from datetime import datetime


metadata = sqlalchemy.MetaData()


users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('email', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('phone', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String),
    sqlalchemy.Column('surname', sqlalchemy.String),
    sqlalchemy.Column('second_name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('hashed_password', sqlalchemy.String),
    sqlalchemy.Column('created', sqlalchemy.DateTime, default=datetime.now()),
)

community_name = sqlalchemy.Table(
    'community_names',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('value', sqlalchemy.Text),
    sqlalchemy.Column('user', sqlalchemy.String,
                      sqlalchemy.ForeignKey('users.id'), nullable=True),
)

base_community_settings = sqlalchemy.Table(
    'base_community_settings',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('current_name', sqlalchemy.String),
    sqlalchemy.Column('quorum_counter', sqlalchemy.Integer),
    sqlalchemy.Column('success_counter', sqlalchemy.String),
)

community = sqlalchemy.Table(
    'community',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('creator', sqlalchemy.String,
                      sqlalchemy.ForeignKey('users.id'), nullable=True),
)

relations_community_name = sqlalchemy.Table(
    'relations_community_settings_names',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('from_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('base_community_settings.id'),
                      nullable=True),
    sqlalchemy.Column('to_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('community_names.id'),
                      nullable=True),
    extend_existing=True,
)

relations_community_settings = sqlalchemy.Table(
    'relations_community_settings',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('from_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('community.id'),
                      nullable=True),
    sqlalchemy.Column('to_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('base_community_settings.id'),
                      nullable=True),
    extend_existing=True,
)

relations_community_users = sqlalchemy.Table(
    'relations_community_users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('from_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('community.id'), nullable=True),
    sqlalchemy.Column('to_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('users.id'), nullable=True),
    extend_existing=True,
)

relations_users_community_settings = sqlalchemy.Table(
    'relations_users_community_settings',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('from_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('users.id'), nullable=True),
    sqlalchemy.Column('to_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('base_community_settings.id'),
                      nullable=True),
    extend_existing=True,
)
