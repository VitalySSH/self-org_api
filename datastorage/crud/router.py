from typing import Type, List, Optional, TypeVar
from enum import Enum

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.interfaces.base import Include
from datastorage.crud.interfaces.list import Filters, Pagination, Orders
from datastorage.crud.utils import update_instance_by_likes
from datastorage.database.base import get_async_session
from datastorage.interfaces import T
from entities.user.model import User

RS = TypeVar('RS')
CS = TypeVar('CS')
US = TypeVar('US')


class Method(Enum):
    get = 'get'
    list = 'list'
    create = 'create'
    update = 'update'
    delete = 'delete'


def get_crud_router(
        model: Type[T],
        read_schema: RS,
        create_schema: CS,
        update_schema: US,
        methods: List[Method],
        is_likes: bool = False,
) -> APIRouter:
    """Вернёт роутер для CRUD-операций."""

    router = APIRouter()

    if Method.get in methods:
        @router.get(
            '/{instance_id}',
            response_model=read_schema,
        )
        async def get_instance(
                instance_id: str,
                include: Include = Query(None),
                current_user: User = Depends(auth_service.get_current_user),
                session: AsyncSession = Depends(get_async_session),
        ) -> read_schema:
            ds = CRUDDataStorage(model=model, session=session)
            instance: model = await ds.get(instance_id=instance_id, include=include)
            if instance:
                if is_likes:
                    return update_instance_by_likes(instance=instance, current_user=current_user)
                else:
                    return instance.to_read_schema()

            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f'Объект модели {model.__name__} с id: {instance_id} не найден',
            )

    if Method.list in methods:
        @router.post(
            '/list',
            response_model=List[read_schema],
        )
        async def list_instances(
                filters: Optional[Filters] = None,
                orders: Optional[Orders] = None,
                pagination: Optional[Pagination] = None,
                include: Optional[Include] = None,
                current_user: User = Depends(auth_service.get_current_user),
                session: AsyncSession = Depends(get_async_session),
        ) -> List[read_schema]:
            ds = CRUDDataStorage(model=model, session=session)
            instances: List[model] = await ds.list(
                filters=filters, orders=orders, pagination=pagination, include=include)
            if is_likes:
                return [update_instance_by_likes(instance=instance, current_user=current_user)
                        for instance in instances]
            else:
                return [instance.to_read_schema() for instance in instances]

    if Method.create in methods:
        @router.post(
            '/create',
            response_model=read_schema,
        )
        async def create_instance(
                body: create_schema,
                current_user: User = Depends(auth_service.get_current_user),
                session: AsyncSession = Depends(get_async_session),
        ) -> read_schema:
            ds = CRUDDataStorage(model=model, session=session)
            instance_to_add: model = await ds.schema_to_model(schema=body)
            relation_fields: List[str] = ds.get_relation_fields(body)
            try:
                new_instance = await ds.create(
                    instance=instance_to_add, relation_fields=relation_fields)
                if is_likes:
                    return update_instance_by_likes(
                        instance=new_instance, current_user=current_user)
                else:
                    return new_instance.to_read_schema()

            except CRUDConflict as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.description,
                )

    if Method.update in methods:
        @router.patch(
            '/{instance_id}',
            dependencies=[Depends(auth_service.get_current_user)],
            status_code=204,
        )
        async def update_instance(
                instance_id: str,
                body: update_schema,
                session: AsyncSession = Depends(get_async_session),
        ) -> None:
            ds = CRUDDataStorage(model=model, session=session)
            try:
                await ds.update(instance_id=instance_id, schema=body)
            except CRUDNotFound as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.description,
                )
            except CRUDConflict as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.description,
                )

    if Method.delete in methods:
        @router.delete(
            '/{instance_id}',
            dependencies=[Depends(auth_service.get_current_user)],
            status_code=204,
        )
        async def delete_instance(
                instance_id: str,
                session: AsyncSession = Depends(get_async_session),
        ) -> None:
            ds = CRUDDataStorage(model=model, session=session)
            try:
                await ds.delete(instance_id)
            except CRUDConflict as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.description,
                )

    return router
