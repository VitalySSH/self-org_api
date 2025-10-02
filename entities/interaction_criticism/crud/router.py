from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import InteractionCriticism
from .schemas import ICrRead, ICrCreate, ICrUpdate

router = get_crud_router(
    model=InteractionCriticism,
    read_schema=ICrRead,
    create_schema=ICrCreate,
    update_schema=ICrUpdate,
    methods=[Method.ALL],
)
