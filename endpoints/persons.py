# from typing import Optional, List
#
# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
#
# from app.crud.database.base import get_db
# from app.crud.database.tables import persons
# from app.crud.datasource.interfaces.list import Filters, Pagination, Orders
# from app.crud.datastorage.person import PersonDataStorage
# from app.endpoints.depends import get_person_datastorage
# from app.models.person import Person
#
# router = APIRouter()
#
#
# @router.get('/', response_model=Person)
# async def get_person_by_id(
#         person_id: str,
#         persons: PersonDataStorage = Depends(get_person_datastorage)):
#     return await persons.get_by_id(person_id)
#
#
# @router.get('/', response_model=Person)
# async def get_person_by_user_id(
#         user_id: str,
#         persons: PersonDataStorage = Depends(get_person_datastorage)):
#     return await persons.get_by_user_id(user_id)
#
#
# @router.post('/list', response_model=List[Person])
# async def get_persons(
#         persons: PersonDataStorage = Depends(get_person_datastorage),
#         filters: Optional[Filters] = None,
#         orders: Optional[Orders] = None,
#         pagination: Optional[Pagination] = None):
#     return await persons.list(
#         filters=filters,
#         orders=orders,
#         pagination=pagination,
#     )
#
#
# @router.post('/', response_model=Person)
# async def create(person: Person,
#                  persons: PersonDataStorage = Depends(get_person_datastorage)):
#     return await persons.create(person)
#
#
# @router.put('/', response_model=Person)
# async def update(person_id: str, person: Person,
#                  persons: PersonDataStorage = Depends(get_person_datastorage)):
#     return await persons.update(person_id, person)
