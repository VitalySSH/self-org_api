from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import User
from .schemas import UserRead, UserCreate, UserUpdate

router = get_crud_router(
    model=User,
    read_schema=UserRead,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
)
