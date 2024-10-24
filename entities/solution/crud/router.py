from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Solution
from .schemas import SolutionRead, SolutionUpdate, SolutionCreate

router = get_crud_router(
    model=Solution,
    read_schema=SolutionRead,
    create_schema=SolutionCreate,
    update_schema=SolutionUpdate,
    methods=[Method.ALL],
)
