import importlib
import inspect
import pkgutil

from typing import List
from sqlalchemy import Column, Table

from crud.database.tables import metadata


def generate_table(_metadata):
    columns: List[Column] = []
    for d1, d2 in _metadata:
        columns.append(
            Column(
                name=d1,
                type_='column_type',
                nullable=True,
                primary_key=d1 == 'id'
            )
        )

    return Table(
        'table_name',
        metadata,
        *columns,
        extend_existing=True
    )


def get_entities(entities_modules=None):
    if not entities_modules:
        entities_modules = ['entities']

    result = []

    for entities_module in entities_modules:
        module = importlib.import_module(entities_module)

        for loader, module_name, error in pkgutil.walk_packages(
                module.__path__, module.__name__ + '.'):
            if not error:
                entity_module = importlib.import_module('.', module_name)
                classes = inspect.getmembers(
                        entity_module, inspect.isclass)
                classes = [cls for class_name, cls in classes
                           if cls.__module__ == entity_module.__name__]
                if len(classes) != 1:
                    assert Exception(
                        f'Модуль {entity_module.__name__} не найден')
                result.append(classes[0])
    return result

