from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import CombinationSourceElement
from .schemas import CSERead, CSECreate, CSEUpdate

router = get_crud_router(
    model=CombinationSourceElement,
    read_schema=CSERead,
    create_schema=CSECreate,
    update_schema=CSEUpdate,
    methods=[Method.ALL],
)
