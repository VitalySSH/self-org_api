from copy import deepcopy
from typing import Type, List, Optional, TypeVar

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from auth.auth import auth_service
from datastorage.crud.dataclasses import PostProcessingData
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.enum import Method
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


def get_crud_router(
        model: Type[T],
        read_schema: RS,
        create_schema: CS,
        update_schema: US,
        methods: List[Method],
        is_likes: bool = False,
        post_processing_data: Optional[PostProcessingData] = None,
) -> APIRouter:
    """Вернёт роутер для CRUD-операций."""

    router = APIRouter()
    is_all_methods = Method.ALL in methods

    if Method.GET in methods or is_all_methods:
        @router.get(
            '/{instance_id}',
            response_model=read_schema,
            status_code=200,
        )
        async def get_instance(
                instance_id: str,
                include: List[str] = Query(None),
                current_user: User = Depends(auth_service.get_current_user),
                session: AsyncSession = Depends(get_async_session),
        ) -> read_schema:
            ds = CRUDDataStorage[model](model=model, session=session)
            instance: model = await ds.get(instance_id=instance_id, include=include)
            if instance:
                if post_processing_data:
                    if Method.GET in post_processing_data.methods:
                        if post_processing_data.include:
                            post_instance: model = await ds.get(
                                instance_id=instance_id, include=post_processing_data.include)
                        else:
                            post_instance = deepcopy(instance)
                        await ds.execute_post_processing(
                            instance=post_instance, post_processing_data=post_processing_data)

                if is_likes:
                    return update_instance_by_likes(instance=instance, current_user=current_user)
                else:
                    return instance.to_read_schema()

            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f'Объект модели {model.__name__} с id: {instance_id} не найден',
            )

    if Method.LIST in methods or is_all_methods:
        @router.post(
            '/list',
            response_model=List[read_schema],
            status_code=200,
        )
        async def list_instances(
                filters: Filters = None,
                orders: Orders = None,
                pagination: Pagination = None,
                include: Include = None,
                current_user: User = Depends(auth_service.get_current_user),
                session: AsyncSession = Depends(get_async_session),
        ) -> List[read_schema]:
            ds = CRUDDataStorage[model](model=model, session=session)
            instances: List[model] = await ds.list(
                filters=filters, orders=orders, pagination=pagination, include=include)
            if is_likes:
                return [update_instance_by_likes(instance=instance, current_user=current_user)
                        for instance in instances]
            else:
                return [instance.to_read_schema() for instance in instances]

    if Method.CREATE in methods or is_all_methods:
        @router.post(
            '/create',
            response_model=read_schema,
            status_code=201,
        )
        async def create_instance(
                body: create_schema,
                current_user: User = Depends(auth_service.get_current_user),
                session: AsyncSession = Depends(get_async_session),
        ) -> read_schema:
            ds = CRUDDataStorage[model](model=model, session=session)
            instance_to_add: model = await ds.schema_to_model(schema=body)
            relation_fields: List[str] = ds.get_relation_fields(body)
            try:
                new_instance = await ds.create(
                    instance=instance_to_add, relation_fields=relation_fields)

                if post_processing_data:
                    if Method.CREATE in post_processing_data.methods:
                        if post_processing_data.include:
                            post_instance: model = await ds.get(
                                instance_id=new_instance.id, include=post_processing_data.include)
                        else:
                            post_instance = deepcopy(new_instance)
                        await ds.execute_post_processing(
                            instance=post_instance, post_processing_data=post_processing_data)

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

    if Method.UPDATE in methods or is_all_methods:
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
            ds = CRUDDataStorage[model](model=model, session=session)
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
            if post_processing_data:
                if Method.UPDATE in post_processing_data.methods:
                    post_instance: model = await ds.get(
                        instance_id=instance_id, include=post_processing_data.include)
                    await ds.execute_post_processing(
                        instance=post_instance, post_processing_data=post_processing_data)

    if Method.DELETE in methods or is_all_methods:
        @router.delete(
            '/{instance_id}',
            dependencies=[Depends(auth_service.get_current_user)],
            status_code=204,
        )
        async def delete_instance(
                instance_id: str,
                session: AsyncSession = Depends(get_async_session),
        ) -> None:
            ds = CRUDDataStorage[model](model=model, session=session)
            try:
                await ds.delete(instance_id)
            except CRUDConflict as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.description,
                )
            if post_processing_data:
                if Method.DELETE in post_processing_data.methods:
                    post_instance: model = await ds.get(
                        instance_id=instance_id, include=post_processing_data.include)
                    await ds.execute_post_processing(
                        instance=post_instance, post_processing_data=post_processing_data)

    return router
