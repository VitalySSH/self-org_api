from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import CommunityName
from .schemas import CommunityNameRead, CommunityNameCreate, CommunityNameUpdate

router = get_crud_router(
    model=CommunityName,
    read_schema=CommunityNameRead,
    create_schema=CommunityNameCreate,
    update_schema=CommunityNameUpdate,
    methods=[Method.ALL],
)
