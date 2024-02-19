# self-org_api

## Установка и запуск приложения

### Разворачивание Django-приложение на локальной машине

Сгенерировать секретные ключи можно здесь: https://djecrety.ir/
- Установите зависимости `pip3 install -r requirements/dev.txt`
- Сравнить состояние БД и моделей `alembic revision --autogenerate -m "commit"` 
- Обновить БД `alembic upgrade 815339b0fdb0`