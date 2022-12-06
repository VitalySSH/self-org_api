import sqlalchemy

from datetime import datetime

metadata = sqlalchemy.MetaData()


users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('email', sqlalchemy.String,
                      primary_key=True, nullable=True),
    sqlalchemy.Column('phone', sqlalchemy.String,
                      primary_key=True, nullable=True),
    sqlalchemy.Column('password', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('created', sqlalchemy.DateTime, default=datetime.now()),
    sqlalchemy.Column('is_active', sqlalchemy.Boolean, default=True),
)

person = sqlalchemy.Table(
    'person',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('user_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('users.id'), nullable=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('surname', sqlalchemy.String, nullable=True),
)

community_settings = sqlalchemy.Table(
    'community_settings',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('suggested_name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('selected_name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('quorum_counter', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('success_counter', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('community', sqlalchemy.String,
                      sqlalchemy.ForeignKey('community.id'),
                      nullable=True),
)

community = sqlalchemy.Table(
    'community',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('creator', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'), nullable=True),
    sqlalchemy.Column('quorum_counter', sqlalchemy.JSON, default={}),
    sqlalchemy.Column('success_counter', sqlalchemy.JSON, default={}),
    sqlalchemy.Column('suggested_names', sqlalchemy.JSON, default={}),
)

relations_persons_community_settings = sqlalchemy.Table(
    'relations_person_community_settings',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('from_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'),
                      nullable=True),
    sqlalchemy.Column('to_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('community_settings.id'),
                      nullable=True),
    extend_existing=True,
)

relations_community_persons = sqlalchemy.Table(
    'relations_community_persons',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('from_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('community.id'), nullable=True),
    sqlalchemy.Column('to_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'), nullable=True),
    extend_existing=True,
)

relations_person_delegates = sqlalchemy.Table(
    'relations_person_delegates',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('from_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'), nullable=True),
    sqlalchemy.Column('to_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'), nullable=True),
    extend_existing=True,
)

relations_person_observed_persons = sqlalchemy.Table(
    'relations_person_observed_persons',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('from_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'), nullable=True),
    sqlalchemy.Column('to_id', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'), nullable=True),
    extend_existing=True,
)
