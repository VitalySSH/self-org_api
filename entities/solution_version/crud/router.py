from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import SolutionVersion
from .schemas import SVRead, SVCreate, SVUpdate

router = get_crud_router(
    model=SolutionVersion,
    read_schema=SVRead,
    create_schema=SVCreate,
    update_schema=SVUpdate,
    methods=[Method.ALL],
)
