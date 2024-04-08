from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.result_voting.schemas import (
    ResultVotingUpdate, ResultVotingRead, ResultVotingCreate
)
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.schemas.interfaces import Include
from datastorage.database.base import get_async_session
from datastorage.database.models import ResultVoting
from datastorage.crud.schemas.list import Filters, Orders, Pagination

router = APIRouter()


@router.get(
    '/get/{result_voting_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ResultVotingRead,
)
async def get_result_voting(
    obj_id: str,
    include: Include = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> ResultVotingRead:
    ds = CRUDDataStorage(model=ResultVoting, session=session)
    obj: ResultVoting = await ds.get(obj_id=obj_id, include=include)
    if obj:
        return obj.to_read_schema()
    raise HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail=f'Сообщество с id: {obj_id} не найдено',
    )


@router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[ResultVotingRead],
)
async def list_result_voting(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    include: Optional[Include] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[ResultVotingRead]:
    ds = CRUDDataStorage(model=ResultVoting, session=session)
    obj_list: List[ResultVoting] = await ds.list(
        filters=filters, orders=orders, pagination=pagination, include=include)
    return [obj.to_read_schema() for obj in obj_list]


@router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ResultVotingRead,
)
async def create_result_voting(
    body: ResultVotingCreate,
    session: AsyncSession = Depends(get_async_session),
) -> ResultVotingRead:
    ds = CRUDDataStorage(model=ResultVoting, session=session)
    obj_to_add: ResultVoting = await ds.schema_to_model(schema=body)
    try:
        new_community = await ds.create(obj_to_add)
        return new_community.to_read_schema()
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.patch(
    '/update/{result_voting_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_result_voting(
    obj_id: str,
    body: ResultVotingUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=ResultVoting, session=session)
    try:
        await ds.update(obj_id=obj_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.delete(
    '/update/{result_voting_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_result_voting(
    obj_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=ResultVoting, session=session)
    try:
        await ds.delete(obj_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
