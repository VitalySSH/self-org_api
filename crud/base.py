from typing import Optional

from databases import Database
from sqlalchemy import Table
from sqlalchemy.sql import Select

from crud.datasource.interfaces.list import Filters, Orders, Pagination


class BaseDataStorage:

    def __init__(self, database: Database):
        self.database = database

    def filtering(
            self, table: Table, filters: Optional[Filters] = None,
                   order: Optional[Orders] = None,
                   pagination: Optional[Pagination] = None) -> Select:
        pass
