from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import CollectiveInteraction
from .schemas import CIRead, CICreate, CIUpdate

router = get_crud_router(
    model=CollectiveInteraction,
    read_schema=CIRead,
    create_schema=CICreate,
    update_schema=CIUpdate,
    methods=[Method.ALL],
)
