from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserCreate, UserUpdate
from auth.security import decrypt_password, hash_password
from datastorage.database.models import User, UserData


class UserService:
    """Сервис для работы с пользователем."""

    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по идентификатору."""
        query = select(User).where(User.id == user_id)

        return await self._session.scalar(query)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по идентификатору."""
        query = select(User).where(User.email == email)

        return await self._session.scalar(query)

    async def get_user_data_by_user_id(self, user_id: str) -> Optional[UserData]:
        """Получить пользователя по идентификатору."""
        query = select(UserData).where(UserData.user_id == user_id)

        return await self._session.scalar(query)

    async def create_user(self, user_data: UserCreate) -> None:
        """Создание пользователя."""
        user = User()
        user.firstname = user_data.firstname
        user.surname = user_data.surname
        user.email = user_data.email
        user.about_me = user_data.about_me
        try:
            self._session.add(user)
            await self._session.flush([user])
            await self._session.refresh(user)
        except Exception as e:
            raise Exception(f'Не удалось создать пользователя: {e}')
        password = decrypt_password(user_data.secret_password)
        hashed_password = hash_password(password)
        user_data = UserData()
        user_data.user = user
        user_data.hashed_password = hashed_password
        try:
            self._session.add(user_data)
            await self._session.commit()
        except Exception as e:
            await self._session.rollback()
            raise Exception(f'Не удалось создать авторизационные данные пользователя: {e}')

    async def update_user(self, user_id: str, user_data: UserUpdate) -> None:
        """Изменение пользователя."""
        user: Optional[User] = await self.get_user_by_id(user_id)
        if not user:
            return

        for key, value in user_data.items():
            setattr(user, key, value)

        try:
            await self._session.commit()
        except Exception as e:
            raise Exception(f'Ошибка обновления пользователя с id {user_id}: {e}')