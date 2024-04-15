from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import DelegateSettings
from .schemas import DelegateSettingsRead, DelegateSettingsCreate, DelegateSettingsUpdate

router = get_crud_router(
    model=DelegateSettings,
    read_schema=DelegateSettingsRead,
    create_schema=DelegateSettingsCreate,
    update_schema=DelegateSettingsUpdate,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
)
