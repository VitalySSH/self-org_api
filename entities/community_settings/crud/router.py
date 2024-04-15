from datastorage.crud.router import get_crud_router, Method
from datastorage.database.models import CommunitySettings
from .schemas import ReadComSettings, UpdateComSettings, CreateComSettings

router = get_crud_router(
    model=CommunitySettings,
    read_schema=ReadComSettings,
    create_schema=CreateComSettings,
    update_schema=UpdateComSettings,
    methods=[
        Method.get,
        Method.list,
        Method.create,
        Method.update,
        Method.delete,
    ],
)
