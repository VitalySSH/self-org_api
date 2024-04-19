from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import VotingResult
from .schemas import ResultVotingRead, ResultVotingCreate, ResultVotingUpdate

router = get_crud_router(
    model=VotingResult,
    read_schema=ResultVotingRead,
    create_schema=ResultVotingCreate,
    update_schema=ResultVotingUpdate,
    methods=[Method.GET, Method.LIST, Method.CREATE, Method.UPDATE, Method.DELETE],
)
