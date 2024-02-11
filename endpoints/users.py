# from typing import Optional, List
#
# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
#
#
# router = APIRouter()
#
#
# @router.get('/{phone}', response_model=User)
# async def get_user_by_phone(
#         phone: str,
#         db: Session = Depends(get_db),
#         users: UserDataStorage = Depends(get_user_datastorage)):
#     return await users.get_by_phone(phone)
#
#
# @router.get('/{email}', response_model=User)
# async def get_user_by_email(
#         email: str,
#         db: Session = Depends(get_db),
#         users: UserDataStorage = Depends(get_user_datastorage)):
#     return await users.get_by_phone(email)
#
#
# @router.post('/list', response_model=List[User])
# async def get_users(
#         users: UserDataStorage = Depends(get_user_datastorage),
#         db: Session = Depends(get_db),
#         filters: Optional[Filters] = None,
#         orders: Optional[Orders] = None,
#         pagination: Optional[Pagination] = None):
#     return await users.list(
#         filters=filters,
#         orders=orders,
#         pagination=pagination,
#     )
#
#
# @router.post('/list-test', response_model=List[User])
# async def get_users(db: Session = Depends(get_db)):
#     return db.query(users).all()
#
#
# @router.post('/', response_model=User)
# async def create(user: User,
#                  db: Session = Depends(get_db),
#                  users: UserDataStorage = Depends(get_user_datastorage)):
#     return await users.create(user)
#
#
# @router.put('/', response_model=User)
# async def update(user_id: str, user: User,
#                  db: Session = Depends(get_db),
#                  users: UserDataStorage = Depends(get_user_datastorage)):
#     return await users.update(user_id, user)
