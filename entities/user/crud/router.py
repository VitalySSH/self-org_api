from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import decrypt_password, hash_password
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.enum import Method
from datastorage.crud.exceptions import CRUDConflict
from datastorage.crud.router import get_crud_router
from datastorage.database.base import get_async_session
from datastorage.database.models import User
from .schemas import UserRead, UserCreate, UserUpdate

router = get_crud_router(
    model=User,
    read_schema=UserRead,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    methods=[Method.GET, Method.LIST, Method.UPDATE, Method.DELETE],
)


@router.post(
    '/',
    response_model=UserRead,
)
async def create_instance(
        body: UserCreate,
        session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    ds = CRUDDataStorage[User](model=User, session=session)
    instance_to_add: User = await ds.schema_to_model(schema=body)
    password = decrypt_password(instance_to_add.hashed_password)
    hashed_password = hash_password(password)
    instance_to_add.hashed_password = hashed_password
    try:
        new_instance = await ds.create(instance=instance_to_add)
        return new_instance.to_read_schema()

    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
