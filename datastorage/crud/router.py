from copy import deepcopy
from typing import Type, List, Optional, TypeVar, Tuple

from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from auth.auth import auth_service
from datastorage.crud.dataclasses import PostProcessingData, ListResponse
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.enum import Method
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.interfaces.base import Include
from datastorage.crud.interfaces.list import Filters, Pagination, Orders
from datastorage.crud.interfaces.schema import ListResponseSchema
from datastorage.database.base import get_async_session
from datastorage.interfaces import T


RS = TypeVar('RS')
CS = TypeVar('CS')
US = TypeVar('US')


def build_post_processing_data(
        current_method: Method,
        post_processing_data: List[PostProcessingData]
) -> Tuple[List[PostProcessingData], List[str]]:
    current_post_processing_data: List[PostProcessingData] = []
    include: List[str] = []
    for post_processing in post_processing_data:
        if current_method in post_processing.methods:
            for incl in post_processing.include or []:
                if incl not in include:
                    include.append(incl)
            current_post_processing_data.append(post_processing)

    return current_post_processing_data, include


def get_crud_router(
        model: Type[T],
        read_schema: RS,
        create_schema: CS,
        update_schema: US,
        methods: List[Method],
        post_processing_data: Optional[List[PostProcessingData]] = None,
) -> APIRouter:
    """Вернёт роутер для CRUD-операций."""

    router = APIRouter()
    is_all_methods = Method.ALL in methods

    if Method.GET in methods or is_all_methods:
        @router.get(
            '/{instance_id}',
            dependencies=[Depends(auth_service.get_current_user)],
            response_model=read_schema,
            status_code=200,
        )
        async def get_instance(
                instance_id: str,
                background_tasks: BackgroundTasks,
                include: List[str] = Query(None),
                session: AsyncSession = Depends(get_async_session),
        ) -> read_schema:
            ds = CRUDDataStorage[model](
                model=model, session=session, background_tasks=background_tasks)
            instance: model = await ds.get(instance_id=instance_id, include=include)
            if instance:
                if post_processing_data:
                    pp_data, include = build_post_processing_data(
                        current_method=Method.GET, post_processing_data=post_processing_data)
                    if pp_data:
                        if include:
                            post_instance: model = await ds.get(
                                instance_id=instance_id, include=include)
                            await ds.invalidate_session()
                        else:
                            post_instance = deepcopy(instance)

                        ds.execute_post_processing(
                            instance=post_instance, post_processing_data=pp_data)

                return instance.to_read_schema()

            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f'Объект модели {model.__name__} с id: {instance_id} не найден',
            )

    if Method.LIST in methods or is_all_methods:
        @router.post(
            '/list',
            dependencies=[Depends(auth_service.get_current_user)],
            response_model=ListResponseSchema[read_schema],  # type: ignore
            status_code=200,
        )
        async def list_instances(
                background_tasks: BackgroundTasks,
                filters: Filters = None,
                orders: Orders = None,
                pagination: Pagination = None,
                include: Include = None,
                session: AsyncSession = Depends(get_async_session),
        ) -> ListResponseSchema[read_schema]:  # type: ignore
            ds = CRUDDataStorage[model](
                model=model, session=session, background_tasks=background_tasks)
            resp: ListResponse[model] = await ds.list(
                filters=filters, orders=orders, pagination=pagination, include=include)

            return ListResponseSchema[read_schema](  # type: ignore
                items=[instance.to_read_schema() for instance in resp.data],
                total=resp.total
            )

    if Method.CREATE in methods or is_all_methods:
        @router.post(
            '/',
            dependencies=[Depends(auth_service.get_current_user)],
            response_model=read_schema,
            status_code=201,
        )
        async def create_instance(
                body: create_schema,
                background_tasks: BackgroundTasks,
                session: AsyncSession = Depends(get_async_session),
        ) -> read_schema:
            ds = CRUDDataStorage[model](
                model=model, session=session, background_tasks=background_tasks)
            instance_to_add: model = await ds.schema_to_model(schema=body)
            relation_fields: List[str] = ds.get_relation_fields(body)
            try:
                new_instance = await ds.create(
                    instance=instance_to_add, relation_fields=relation_fields)

                if post_processing_data:
                    pp_data, include = build_post_processing_data(
                        current_method=Method.CREATE, post_processing_data=post_processing_data)
                    if pp_data:
                        if include:
                            post_instance: model = await ds.get(
                                instance_id=new_instance, include=include)
                            await ds.invalidate_session()
                        else:
                            post_instance = deepcopy(new_instance)

                        ds.execute_post_processing(
                            instance=post_instance, post_processing_data=pp_data)

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
                background_tasks: BackgroundTasks,
                session: AsyncSession = Depends(get_async_session),
        ) -> None:
            ds = CRUDDataStorage[model](
                model=model, session=session, background_tasks=background_tasks)
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
                pp_data, include = build_post_processing_data(
                    current_method=Method.UPDATE, post_processing_data=post_processing_data)
                if pp_data:
                    post_instance: model = await ds.get(
                        instance_id=instance_id, include=include)
                    await ds.invalidate_session()
                    ds.execute_post_processing(
                        instance=post_instance, post_processing_data=pp_data)

    if Method.DELETE in methods or is_all_methods:
        @router.delete(
            '/{instance_id}',
            dependencies=[Depends(auth_service.get_current_user)],
            status_code=204,
        )
        async def delete_instance(
                instance_id: str,
                background_tasks: BackgroundTasks,
                session: AsyncSession = Depends(get_async_session),
        ) -> None:
            ds = CRUDDataStorage[model](
                model=model, session=session, background_tasks=background_tasks)
            try:
                await ds.delete(instance_id)
            except CRUDConflict as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.description,
                )
            if post_processing_data:
                pp_data, include = build_post_processing_data(
                    current_method=Method.DELETE, post_processing_data=post_processing_data)
                if pp_data:
                    await ds.invalidate_session()
                    ds.execute_post_processing(
                        instance=None, post_processing_data=pp_data, instance_id=instance_id)

    return router
