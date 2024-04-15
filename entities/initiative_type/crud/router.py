from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import InitiativeType
from .schemas import InitiativeTypeRead, InitiativeTypeCreate, InitiativeTypeUpdate

router = get_crud_router(
    model=InitiativeType,
    read_schema=InitiativeTypeRead,
    create_schema=InitiativeTypeCreate,
    update_schema=InitiativeTypeUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
)
