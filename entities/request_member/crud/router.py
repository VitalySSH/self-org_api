from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import RequestMember
from .schemas import RequestMemberRead, RequestMemberCreate, RequestMemberUpdate


router = get_crud_router(
    model=RequestMember,
    read_schema=RequestMemberRead,
    create_schema=RequestMemberCreate,
    update_schema=RequestMemberUpdate,
    methods=[Method.ALL],
)
