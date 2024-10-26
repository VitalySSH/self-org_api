# API проекта "Тебе решать"

## Необходимые инструменты

* [git](https://github.com/git-guides/install-git/) 
* [pip](https://pypi.org/project/pip/)
* [pip-tools](https://github.com/jazzband/pip-tools)
* [virtual env](https://docs.python.org/3/tutorial/venv.html)
* [docker](https://docs.docker.com/engine/)
* [docker-compose](https://docs.docker.com/compose/)

## Установка и запуск приложения

### Разворачивание API-приложения на локальной машине
* Установить виртуальное окружение: python3 -m venv venv
* Активировать виртуальное окружение: source venv/bin/activate
* Установите зависимости `pip3 install -r requirements/dev.txt`
* Создать файл .env в корневой директории и настроить переменные окружения для подключения БД и запуска приложения
``` 
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=
JWT_SECRET_KEY=
PASSWORD_SECRET_KEY=
JWT_LIFE_TIME_SECONDS=
COOKIE_TOKEN_NAME=
```
> Сгенерировать SECRET_KEYS можно здесь: https://jwtsecret.com/
* Создать чистую БД PostgreSQL
* Если в папке migrations/versions отсутствует файл с конфигурацией БД, то создайте его командой `alembic revision --autogenerate -m "init commit"`
* Создать таблицы в БД `alembic upgrade c60a9cfd7708` (или другой uuid конфигурации)
* Наполнить БД предустановленными значениями командой `python3.12 app/init_db_data.py`
* Запустить API командой `python3.12 app/main.py`

## Технологии
- [Python 3.12](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [NGINX](https://nginx.org)