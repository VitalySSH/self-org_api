from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import InitiativeType
from .schemas import InitiativeTypeRead, InitiativeTypeCreate, InitiativeTypeUpdate

router = get_crud_router(
    model=InitiativeType,
    read_schema=InitiativeTypeRead,
    create_schema=InitiativeTypeCreate,
    update_schema=InitiativeTypeUpdate,
    methods=[Method.ALL],
)
