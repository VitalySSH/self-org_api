from datastorage.crud.dataclasses import PostProcessingData
from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import UserVotingResult
from .schemas import UserVRRead, UserVRCreate, UserVRUpdate
from ..ao.datastorage import UserVotingResultDS

post_processing = [
    PostProcessingData(
        data_storage=UserVotingResultDS,
        methods=[Method.UPDATE],
        instance_attr='id',
        func_name='recount_vote',
    ),
]

router = get_crud_router(
    model=UserVotingResult,
    read_schema=UserVRRead,
    create_schema=UserVRCreate,
    update_schema=UserVRUpdate,
    methods=[Method.ALL],
    post_processing_data=post_processing,
)
