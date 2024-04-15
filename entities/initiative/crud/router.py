from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import Initiative
from .schemas import InitiativeRead, InitiativeCreate, InitiativeUpdate

router = get_crud_router(
    model=Initiative,
    read_schema=InitiativeRead,
    create_schema=InitiativeCreate,
    update_schema=InitiativeUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
    is_likes=True,
)
