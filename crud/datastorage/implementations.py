from databases import Database

from crud.datastorage.interfaces import Datastorage
from crud.datastorage.mixins import CrudOperationsMixin


class DataStorageImpl(Datastorage, CrudOperationsMixin):

    def __init__(self, database: Database):
        self.database = database
