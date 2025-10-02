from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Challenge
from .schemas import ChallengeRead, ChallengeCreate, ChallengeUpdate

router = get_crud_router(
    model=Challenge,
    read_schema=ChallengeRead,
    create_schema=ChallengeCreate,
    update_schema=ChallengeUpdate,
    methods=[Method.ALL],
)
