from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import UserCommunitySettings
from .schemas import UserCsRead, UserCsCreate, UserCsUpdate

router = get_crud_router(
    model=UserCommunitySettings,
    read_schema=UserCsRead,
    create_schema=UserCsCreate,
    update_schema=UserCsUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
)
