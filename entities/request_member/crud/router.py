from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import RequestMember
from datastorage.crud.dataclasses import PostProcessingData
from .schemas import (
    RequestMemberRead, RequestMemberCreate, RequestMemberUpdate
)
from ..ao.datastorage import RequestMemberDS


post_processing = [
    PostProcessingData(
        data_storage=RequestMemberDS,
        methods=[Method.CREATE],
        instance_attr='id',
        func_name='add_request_member_to_settings',
    ),
    PostProcessingData(
        data_storage=RequestMemberDS,
        methods=[Method.UPDATE],
        instance_attr='id',
        func_name='update_parent_request_member',
    ),
    PostProcessingData(
        data_storage=RequestMemberDS,
        methods=[Method.DELETE],
        func_name='delete_child_request_members',
    ),
]


router = get_crud_router(
    model=RequestMember,
    read_schema=RequestMemberRead,
    create_schema=RequestMemberCreate,
    update_schema=RequestMemberUpdate,
    methods=[Method.ALL],
    post_processing_data=post_processing,
)
