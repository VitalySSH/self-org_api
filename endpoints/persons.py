from typing import Optional, List

from fastapi import APIRouter, Depends

from crud.datasource.interfaces.list import Filters, Pagination, Orders
from crud.datastorage.person import PersonDataStorage
from crud.models.person import Person
from endpoints.depends import get_person_datastorage

router = APIRouter()


@router.get('/', response_model=Person)
async def get_person_by_id(
        id: str,
        persons: PersonDataStorage = Depends(get_person_datastorage)):
    return await persons.get_by_id(id)


@router.get('/', response_model=Person)
async def get_person_by_user_id(
        user_id: str,
        persons: PersonDataStorage = Depends(get_person_datastorage)):
    return await persons.get_by_user_id(user_id)


@router.post('/list', response_model=List[Person])
async def get_persons(
        persons: PersonDataStorage = Depends(get_person_datastorage),
        filters: Optional[Filters] = None,
        orders: Optional[Orders] = None,
        pagination: Optional[Pagination] = None):
    return await persons.list(
        filters=filters,
        orders=orders,
        pagination=pagination,
    )


@router.post('/', response_model=Person)
async def create(person: Person,
                 persons: PersonDataStorage = Depends(get_person_datastorage)):
    return await persons.create(person)


@router.put('/', response_model=Person)
async def update(id: str, person: Person,
                 persons: PersonDataStorage = Depends(get_person_datastorage)):
    return await persons.update(id, person)
