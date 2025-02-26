from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import VotingResult
from .schemas import VResultRead, VResultCreate, VResultUpdate

router = get_crud_router(
    model=VotingResult,
    read_schema=VResultRead,
    create_schema=VResultCreate,
    update_schema=VResultUpdate,
    methods=[Method.ALL],
)
