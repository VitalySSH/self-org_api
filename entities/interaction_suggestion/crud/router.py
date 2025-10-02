from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import InteractionSuggestion
from .schemas import ISRead, ISCreate, ISUpdate

router = get_crud_router(
    model=InteractionSuggestion,
    read_schema=ISRead,
    create_schema=ISCreate,
    update_schema=ISUpdate,
    methods=[Method.ALL],
)
