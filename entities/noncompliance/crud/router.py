from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Noncompliance
from .schemas import (
    NoncomplianceRead, NoncomplianceCreate, NoncomplianceUpdate
)

router = get_crud_router(
    model=Noncompliance,
    read_schema=NoncomplianceRead,
    create_schema=NoncomplianceCreate,
    update_schema=NoncomplianceUpdate,
    methods=[Method.ALL],
)
