from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import VotingOption
from .schemas import VotingOptionRead, VotingOptionCreate, VotingOptionUpdate

router = get_crud_router(
    model=VotingOption,
    read_schema=VotingOptionRead,
    create_schema=VotingOptionCreate,
    update_schema=VotingOptionUpdate,
    methods=[Method.ALL],
)
