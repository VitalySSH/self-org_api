from fastapi import APIRouter, Depends

from auth.auth import auth_service
from auth.models.user import User
from entities.rule.ao.dataclasses import CreatingNewRule
from entities.rule.ao.datastorage import RuleDS

router = APIRouter()


@router.post(
    '/create_rule',
    status_code=201,
)
async def create_rule(
    payload: CreatingNewRule,
    current_user: User = Depends(auth_service.get_current_user),
) -> None:
    ds = RuleDS()
    async with ds.session_scope():
        current_user = await ds.merge_into_session(current_user)
        await ds.create_rule(data=payload, creator=current_user)
