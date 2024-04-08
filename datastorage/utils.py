import importlib
import inspect
import pkgutil
import uuid
from typing import List, cast

from fastapi import APIRouter

from datastorage.dataclasses import RouterParams


def build_uuid() -> str:
    return str(uuid.uuid4())


def get_routers() -> List[RouterParams]:
    entities_module = 'datastorage.crud.entities'
    result: List[RouterParams] = []
    module = importlib.import_module(entities_module)

    for loader, module_name, error in pkgutil.walk_packages(
            module.__path__, module.__name__ + '.'):
        if not error:
            entity_module = importlib.import_module('.', module_name)
            classes = inspect.getmembers(entity_module)
            filtered = list(filter(lambda it: isinstance(it[1], APIRouter), classes))
            if filtered:
                entity_name = module_name.split('.')[-2]
                router_params = RouterParams(
                    prefix=f'/{entity_name}', tags=[f'CRUD {entity_name}'],
                    router=cast(APIRouter, filtered[0][1])
                )
                result.append(router_params)

    return result
