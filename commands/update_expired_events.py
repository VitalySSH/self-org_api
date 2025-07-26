import asyncio
from datetime import date

from datastorage.consts import Code
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.interfaces.list import Operation, Filter
from entities.initiative.model import Initiative
from entities.status.model import Status


async def update_expired_events():
    print(
        f"[{date.today()}] Запуск команды обновления просроченных событий..."
    )

    initiative_ds = CRUDDataStorage(model=Initiative)

    async with initiative_ds.session_scope():
        try:
            completed_status_filters = [
                Filter(field='code', op=Operation.EQ,
                            val=Code.EVENT_COMPLETED)
            ]
            completed_status = await initiative_ds.first(
                filters=completed_status_filters,
                model=Status
            )

            if not completed_status:
                print(
                    f'Статус с кодом "{Code.EVENT_COMPLETED}" не найден в базе данных')
                return

            current_date = date.today()
            filters = [
                Filter(field='is_one_day_event', op=Operation.EQ, val=True),
                Filter(field='event_date', op=Operation.LT,
                            val=current_date.isoformat()),
                Filter(field='status.code', op=Operation.NOT_EQ,
                            val=Code.EVENT_COMPLETED)
            ]

            initiatives_response = await initiative_ds.list(
                filters=filters,
                include=['status']
            )

            initiatives_to_update = initiatives_response.data

            if not initiatives_to_update:
                print('Не найдено инициатив для обновления статуса')
                return

            print(
                f'Найдено {len(initiatives_to_update)} инициатив для обновления статуса')

            updated_count = 0
            for initiative in initiatives_to_update:
                old_status_code = getattr(initiative.status, "code", "unknown")

                initiative.status = completed_status
                updated_count += 1

                print(f'Обновлена инициатива ID: {initiative.id}, '
                      f'tracker: {initiative.tracker}, '
                      f'event_date: {initiative.event_date}, '
                      f'старый статус: {old_status_code} -> '
                      f'новый статус: {Code.EVENT_COMPLETED}')

            print(f'Успешно обновлено {updated_count} инициатив')

        except Exception as e:
            print(
                f'Ошибка при выполнении команды обновления статусов: {e.__str__()}')


if __name__ == '__main__':
    asyncio.run(update_expired_events())
