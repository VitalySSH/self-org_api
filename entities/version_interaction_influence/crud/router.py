from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import VersionInteractionInfluence
from .schemas import VIIRead, VIICreate, VIIUpdate

router = get_crud_router(
    model=VersionInteractionInfluence,
    read_schema=VIIRead,
    create_schema=VIICreate,
    update_schema=VIIUpdate,
    methods=[Method.ALL],
)
