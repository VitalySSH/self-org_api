from datastorage.crud.dataclasses import PostProcessingData
from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import UserCommunitySettings
from .schemas import UserCsRead, UserCsCreate, UserCsUpdate
from datastorage.database.models import Community
from ...community.ao.data_storage import CommunityDS


post_processing = PostProcessingData(
    data_storage=CommunityDS,
    model=Community,
    methods=[Method.CREATE, Method.UPDATE, Method.DELETE],
    func_name='change_community_settings',
    instance_attr='community_id',
)

router = get_crud_router(
    model=UserCommunitySettings,
    read_schema=UserCsRead,
    create_schema=UserCsCreate,
    update_schema=UserCsUpdate,
    methods=[Method.GET, Method.LIST, Method.CREATE, Method.UPDATE, Method.DELETE],
    post_processing_data=post_processing,
)
