from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import Opinion
from .schemas import OpinionRead, OpinionUpdate, OpinionCreate

router = get_crud_router(
    model=Opinion,
    read_schema=OpinionRead,
    create_schema=OpinionCreate,
    update_schema=OpinionUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
    is_likes=True,
)
