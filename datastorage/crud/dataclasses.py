from dataclasses import dataclass
from typing import Optional

from datastorage.interfaces.list import Filters, Orders, Pagination


@dataclass
class ListData:
    filters: Optional[Filters] = None
    orders: Optional[Orders] = None
    pagination: Optional[Pagination] = None
