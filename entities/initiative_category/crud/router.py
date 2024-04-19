from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import InitiativeCategory
from .schemas import InitCategoryRead, InitCategoryCreate, InitCategoryUpdate

router = get_crud_router(
    model=InitiativeCategory,
    read_schema=InitCategoryRead,
    create_schema=InitCategoryCreate,
    update_schema=InitCategoryUpdate,
    methods=[Method.GET, Method.LIST, Method.CREATE, Method.UPDATE, Method.DELETE],
)
