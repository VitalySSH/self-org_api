from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from auth.models.user import User
from datastorage.database.base import get_async_session
from entities.rule.ao.dataclasses import CreatingNewRule
from entities.rule.ao.datastorage import RuleDS
from entities.rule.model import Rule

router = APIRouter()


@router.post(
    '/create_rule',
    status_code=201,
)
async def create_rule(
    payload: CreatingNewRule,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = RuleDS(model=Rule, session=session)
    await ds.create_rule(data=payload, creator=current_user)
