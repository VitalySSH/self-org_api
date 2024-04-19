from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Community
from .schemas import CommunityRead, CommunityCreate, CommunityUpdate

router = get_crud_router(
    model=Community,
    read_schema=CommunityRead,
    create_schema=CommunityCreate,
    update_schema=CommunityUpdate,
    methods=[Method.GET, Method.LIST, Method.CREATE, Method.UPDATE, Method.DELETE],
)
