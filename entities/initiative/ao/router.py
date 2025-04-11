from fastapi import APIRouter, Depends

from auth.auth import auth_service
from auth.models.user import User
from entities.initiative.ao.dataclasses import CreatingNewInitiative
from entities.initiative.ao.datastorage import InitiativeDS

router = APIRouter()


@router.post(
    '/create_initiative',
    status_code=201,
)
async def create_initiative(
    payload: CreatingNewInitiative,
    current_user: User = Depends(auth_service.get_current_user),
) -> None:
    ds = InitiativeDS()
    async with ds.session_scope():
        await ds.create_initiative(data=payload, creator=current_user)
