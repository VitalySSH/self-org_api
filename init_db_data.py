from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.base import async_session_maker
from datastorage.database.default_data import STATUSES
from entities.status.model import Status


if __name__ == '__main__':
    try:
        session = async_session_maker()
        ds = CRUDDataStorage(model=Status, session=session)
        for entity_data in STATUSES:
            status = Status()
            status.name = entity_data.get('name')
            status.code = entity_data.get('code')
            await ds.create(status)
        print('Статусы добавлены')
    except Exception as e:
        print(f'Не удалось добавить статусы: {e}')
