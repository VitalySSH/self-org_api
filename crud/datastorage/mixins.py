import json
from typing import Optional, List

from sqlalchemy import Table, func, text
from sqlalchemy.sql import Select
from sqlalchemy.sql.base import ImmutableColumnCollection

from crud.datasource.interfaces.list import Filters, Operations, Orders, \
    Pagination, Directions


class CrudOperationsMixin:
    MAX_PAGE_SIZE = 20
    DEFAULT_INDEX = 1

    def query_for_list(self, table: Table,
                       filters: Optional[Filters],
                       orders: Optional[Orders],
                       pagination: Optional[Pagination]) -> Select:
        _limit = pagination.get('limit') if pagination else self.MAX_PAGE_SIZE
        _skip = pagination.get('skip') if pagination else self.DEFAULT_INDEX
        query = table.select().limit(_limit)
        query = query.offset(_skip)
        if filters:
            query = self.__filtering(query, table.c, filters, orders)

        if not filters and orders:
            query = query.filter().order_by(*self.__get_order_params(orders))

        return query

    def __filtering(self, query: Select,
                    column: ImmutableColumnCollection,
                    filters: Optional[Filters],
                    orders: Optional[Orders]) -> Select:
        params = []
        for _filter in filters or []:
            field = getattr(column, _filter.get('field'))
            operation = _filter.get('op')
            value = _filter.get('val')
            if operation == Operations.EQ:
                params.append(field == value)
            elif operation == Operations.NOT_EQ:
                params.append(field != value)
            elif operation == Operations.IN:
                params.append(field.in_(json.loads(value)))
            elif operation == Operations.NOT_IN:
                params.append(field.notin_(json.loads(value)))
            elif operation == Operations.LIKE:
                params.append(field.like(f'%{value}%'))
            elif operation == Operations.ILIKE:
                params.append(field.ilike(f'%{value}%'))
            elif operation == Operations.GT:
                params.append(field > value)
            elif operation == Operations.GTE:
                params.append(field >= value)
            elif operation == Operations.LT:
                params.append(field < value)
            elif operation == Operations.LTE:
                params.append(field <= value)
            elif operation == Operations.IEQ:
                params.append(func.lower(field) == func.lower(value))
            elif operation == Operations.NULL:
                params.append(field.is_(None) if value else field.isnot(None))
            elif operation == Operations.BETWEEN:
                params.append(field.between(*json.loads(value)))

        return query.filter(*params).order_by(*self.__get_order_params(orders))

    def __get_order_params(self, orders: Optional[Orders] = None) -> List[str]:
        params = []
        for order in orders or []:
            field_name = order.get('field')
            direction = order.get('direction')
            if direction == Directions.DESC:
                params.append(text(f'{field_name} desc'))
            else:
                params.append(text(f'{field_name} asc'))

        return params
