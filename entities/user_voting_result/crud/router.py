from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import UserVotingResult
from .schemas import UserVRRead, UserVRCreate, UserVRUpdate

router = get_crud_router(
    model=UserVotingResult,
    read_schema=UserVRRead,
    create_schema=UserVRCreate,
    update_schema=UserVRUpdate,
    methods=[Method.ALL],
)
