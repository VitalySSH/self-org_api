from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Category
from .schemas import CategoryRead, CategoryCreate, CategoryUpdate

router = get_crud_router(
    model=Category,
    read_schema=CategoryRead,
    create_schema=CategoryCreate,
    update_schema=CategoryUpdate,
    methods=[Method.ALL],
)
