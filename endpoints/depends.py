from crud.database.base import database
from crud.datastorage.person import PersonDataStorage
from crud.datastorage.users import UserDataStorage


def get_user_datastorage() -> UserDataStorage:
    return UserDataStorage(database)


def get_person_datastorage() -> PersonDataStorage:
    return PersonDataStorage(database)
