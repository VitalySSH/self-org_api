from crud.database.base import database
from crud.users import UserDataStorage


def get_user_datastorage() -> UserDataStorage:
    return UserDataStorage(database)
