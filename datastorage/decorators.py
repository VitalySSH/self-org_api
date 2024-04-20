import functools
import inspect

from sqlalchemy.ext.asyncio import AsyncSession

from datastorage.base import DataStorage
from datastorage.database.base import get_async_session
from datastorage.enum import SessionAction


async def get_session(self: DataStorage) -> AsyncSession:
    if self._session and self._session.is_active:
        await self._session.close()
    self._session = await anext(get_async_session())
    return self._session


def ds_async_with_session(action: SessionAction = SessionAction.CLOSE):
    """Закрывает сессию или транзакцию,
    после или перед выполнением метода,
    для потомков класса DataStorage.
     """
    def decorator(function):
        @functools.wraps(function)
        async def wrapper(self, *args, **kwargs):
            if action != SessionAction.INVALIDATE_START:
                if not self._session:
                    session = await get_session(self)
                    self.set_session(session)
            else:
                await self._session.invalidate()
            if inspect.iscoroutinefunction(function):
                result = await function(self, *args, **kwargs)
            else:
                raise Exception(f'Функция {function.__name__}, к которой применён декоратор '
                                f'@ds_async_with_session, не является асинхронной')
            if action == SessionAction.CLOSE:
                await self._session.close()
            elif action == SessionAction.INVALIDATE:
                await self._session.invalidate()
            return result

        return wrapper

    return decorator
