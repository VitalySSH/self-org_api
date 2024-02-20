from dataclasses import dataclass
from typing import Optional

from datastorage.interfaces.list import Filters, Orders, Pagination


@dataclass
class ListData:
    filters: Optional[Filters]
    orders: Optional[Orders]
    pagination: Optional[Pagination]
