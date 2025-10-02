from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import InteractionCombination
from .schemas import ICRead, ICCreate, ICUpdate

router = get_crud_router(
    model=InteractionCombination,
    read_schema=ICRead,
    create_schema=ICCreate,
    update_schema=ICUpdate,
    methods=[Method.ALL],
)
