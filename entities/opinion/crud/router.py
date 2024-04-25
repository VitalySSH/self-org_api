from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Opinion
from .schemas import OpinionRead, OpinionUpdate, OpinionCreate

router = get_crud_router(
    model=Opinion,
    read_schema=OpinionRead,
    create_schema=OpinionCreate,
    update_schema=OpinionUpdate,
    methods=[Method.ALL],
    is_likes=True,
)
