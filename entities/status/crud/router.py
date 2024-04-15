from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import Status
from .schemas import StatusRead, StatusCreate, StatusUpdate


router = get_crud_router(
    model=Status,
    read_schema=StatusRead,
    create_schema=StatusCreate,
    update_schema=StatusUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
)
