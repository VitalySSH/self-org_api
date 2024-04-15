from datastorage.crud.router import Method, get_crud_router
from datastorage.database.models import VotingResult
from .schemas import ResultVotingRead, ResultVotingCreate, ResultVotingUpdate

router = get_crud_router(
    model=VotingResult,
    read_schema=ResultVotingRead,
    create_schema=ResultVotingCreate,
    update_schema=ResultVotingUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
)
