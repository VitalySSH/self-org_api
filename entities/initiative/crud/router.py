from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Initiative
from .schemas import InitiativeRead, InitiativeCreate, InitiativeUpdate

router = get_crud_router(
    model=Initiative,
    read_schema=InitiativeRead,
    create_schema=InitiativeCreate,
    update_schema=InitiativeUpdate,
    methods=[Method.ALL],
    is_likes=True,
)
