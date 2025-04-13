import asyncio

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.default_data import STATUSES
from entities.status.model import Status


async def create_statuses():
    ds = CRUDDataStorage(model=Status)
    async with ds.session_scope():
        try:
            for entity_data in STATUSES:
                status = Status()
                status.name = entity_data.get('name')
                status.code = entity_data.get('code')
                await ds.create(status)
            print('Статусы добавлены')
        except Exception as e:
            print(f'Не удалось добавить статусы: {e.__str__()}')


if __name__ == '__main__':
    asyncio.run(create_statuses())
