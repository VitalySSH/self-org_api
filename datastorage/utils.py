import importlib
import inspect
import pkgutil
import uuid
from typing import List, cast

from fastapi import APIRouter

from datastorage.dataclasses import RouterParams


def build_uuid() -> str:
    return str(uuid.uuid4())


def get_entities_routers() -> List[RouterParams]:
    entities_module = 'entities'
    result: List[RouterParams] = []
    module = importlib.import_module(entities_module)

    for loader, module_name, error in pkgutil.walk_packages(
            module.__path__, module.__name__ + '.'):
        if not error:
            entity_module = importlib.import_module('.', module_name)
            members = inspect.getmembers(entity_module)
            filtered = list(filter(lambda it: isinstance(it[1], APIRouter), members))
            if filtered:
                is_crud = module_name.split('.')[-2] == 'crud'
                entity_name = module_name.split('.')[1]
                prefix = f'/crud/{entity_name}' if is_crud else f'/ao/{entity_name}'
                router_params = RouterParams(
                    prefix=prefix,
                    tags=[f'entity {entity_name}'],
                    router=cast(APIRouter, filtered[0][1])
                )
                result.append(router_params)

    return result
