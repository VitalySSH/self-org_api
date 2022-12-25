import sqlalchemy


metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('email', sqlalchemy.String, nullable=True, unique=True),
    sqlalchemy.Column('phone', sqlalchemy.String, nullable=True, unique=True),
    sqlalchemy.Column('password', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('created', sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column('is_active', sqlalchemy.Boolean, nullable=True),
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
    sqlalchemy.Column('name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('description', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('quorum', sqlalchemy.SmallInteger, nullable=True),
    sqlalchemy.Column('vote', sqlalchemy.SmallInteger, nullable=True),
)

community = sqlalchemy.Table(
    'community',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('creator', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'), nullable=True),
    sqlalchemy.Column('default_name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('default_description', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('current_name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('current_description', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('current_quorum', sqlalchemy.SmallInteger, nullable=True),
    sqlalchemy.Column('current_vote', sqlalchemy.SmallInteger, nullable=True),
    sqlalchemy.Column('created', sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column('updated', sqlalchemy.DateTime, nullable=True),
)

voting = sqlalchemy.Table(
    'voting',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True, unique=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('description', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('type', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('status', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('result', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('is_deadline', sqlalchemy.Boolean, nullable=True),
    sqlalchemy.Column('creator', sqlalchemy.String,
                      sqlalchemy.ForeignKey('person.id'), nullable=True),
    sqlalchemy.Column('created', sqlalchemy.DateTime, nullable=True),
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
