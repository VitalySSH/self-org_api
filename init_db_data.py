import asyncio
from typing import Dict

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.default_data import STATUSES
from entities.status.model import Status


async def create_statuses():
    """Создает статусы с проверкой на дублирование."""
    ds = CRUDDataStorage(model=Status)
    async with ds.session_scope():
        try:
            existing_statuses_response = await ds.list()
            existing_statuses = existing_statuses_response.data

            existing_by_code: Dict[str, Status] = {
                status.code: status for status in existing_statuses
            }

            created_count = 0
            updated_count = 0
            unchanged_count = 0

            print(f'Обработка {len(STATUSES)} статусов...')
            print('-' * 60)

            for entity_data in STATUSES:
                code = entity_data.get('code')
                name = entity_data.get('name')

                if not code or not name:
                    print(
                        f'Пропущен статус с неполными данными: {entity_data}')
                    continue

                existing_status = existing_by_code.get(code)

                if existing_status is None:
                    try:
                        status = Status()
                        status.name = name
                        status.code = code
                        await ds.create(status)
                        created_count += 1
                        print(f'✓ СОЗДАН: code="{code}", name="{name}"')
                    except Exception as e:
                        print(
                            f'✗ Ошибка создания статуса code="{code}": {e.__str__()}')

                else:
                    if existing_status.name != name:
                        try:
                            old_name = existing_status.name
                            existing_status.name = name
                            updated_count += 1
                            print(f'↻ ОБНОВЛЕН: code="{code}", '
                                  f'name: "{old_name}" → "{name}"')
                        except Exception as e:
                            print(
                                f'✗ Ошибка обновления статуса code="{code}": {e.__str__()}')
                    else:
                        unchanged_count += 1
                        print(f'= БЕЗ ИЗМЕНЕНИЙ: code="{code}", name="{name}"')

            print('-' * 60)
            print(f'Результат обработки статусов:')
            print(f'• Создано новых: {created_count}')
            print(f'• Обновлено: {updated_count}')
            print(f'• Без изменений: {unchanged_count}')
            print(
                f'• Всего обработано: {created_count + updated_count + unchanged_count}')

        except Exception as e:
            print(f'Критическая ошибка при обработке статусов: {e.__str__()}')


if __name__ == '__main__':
    asyncio.run(create_statuses())
