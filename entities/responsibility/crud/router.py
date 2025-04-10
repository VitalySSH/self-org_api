from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Responsibility
from .schemas import (
    ResponsibilityRead, ResponsibilityCreate, ResponsibilityUpdate
)

router = get_crud_router(
    model=Responsibility,
    read_schema=ResponsibilityRead,
    create_schema=ResponsibilityCreate,
    update_schema=ResponsibilityUpdate,
    methods=[Method.ALL],
)
