from datastorage.crud.enum import Method
from datastorage.crud.router import get_crud_router
from datastorage.database.models import Rule
from .schemas import RuleRead, RuleCreate, RuleUpdate

router = get_crud_router(
    model=Rule,
    read_schema=RuleRead,
    create_schema=RuleCreate,
    update_schema=RuleUpdate,
    methods=[Method.ALL],
)
