from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import UserVotingResult
from .schemas import VResultRead, VResultCreate, VResultUpdate

router = get_crud_router(
    model=UserVotingResult,
    read_schema=VResultRead,
    create_schema=VResultCreate,
    update_schema=VResultUpdate,
    methods=[Method.ALL],
)
