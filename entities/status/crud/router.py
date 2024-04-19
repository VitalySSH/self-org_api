from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Status
from .schemas import StatusRead, StatusCreate, StatusUpdate


router = get_crud_router(
    model=Status,
    read_schema=StatusRead,
    create_schema=StatusCreate,
    update_schema=StatusUpdate,
    methods=[Method.GET, Method.LIST, Method.CREATE, Method.UPDATE, Method.DELETE],
)
