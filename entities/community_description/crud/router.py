from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import CommunityDescription
from .schemas import CommunityDescRead, CommunityDescCreate, CommunityDescUpdate

router = get_crud_router(
    model=CommunityDescription,
    read_schema=CommunityDescRead,
    create_schema=CommunityDescCreate,
    update_schema=CommunityDescUpdate,
    methods=[Method.ALL],
)
