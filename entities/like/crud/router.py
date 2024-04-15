from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import Like
from .schemas import LikeRead, LikeUpdate, LikeCreate

router = get_crud_router(
    model=Like,
    read_schema=LikeRead,
    create_schema=LikeCreate,
    update_schema=LikeUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
)
