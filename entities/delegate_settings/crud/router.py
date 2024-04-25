from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import DelegateSettings
from .schemas import DelegateSettingsRead, DelegateSettingsCreate, DelegateSettingsUpdate

router = get_crud_router(
    model=DelegateSettings,
    read_schema=DelegateSettingsRead,
    create_schema=DelegateSettingsCreate,
    update_schema=DelegateSettingsUpdate,
    methods=[Method.ALL],
)
