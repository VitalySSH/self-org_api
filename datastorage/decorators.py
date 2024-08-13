import functools
import inspect

from datastorage.database.base import async_session_maker


def ds_async_with_new_session(function):
    """Создаёт новую сессию и делает недействительной транзакцию
     сессии после выполнения метода, для потомков класса DataStorage.
     """
    @functools.wraps(function)
    async def wrapper(self, *args, **kwargs):
        if not self._session:
            session = async_session_maker()
            self.set_session(session)
        if inspect.iscoroutinefunction(function):
            result = await function(self, *args, **kwargs)
        else:
            raise Exception(f'Функция {function.__name__}, к которой применён декоратор '
                            f'@ds_async_with_new_session, не является асинхронной')
        await self.invalidate_session()
        return result

    return wrapper
