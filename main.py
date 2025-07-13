import logging
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import auth_router
from core import config
from core.config import HOST, PORT
from datastorage.utils import get_entities_routers
from filestorage.router import file_router

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

app = FastAPI(
    title='UtU API',
    description='Платформа для раскрытия потенциала коллективного интеллекта',
    summary=(
        'Экспериментальная технологическая система, которая помогает группам '
        'людей, от локальных сообществ до организаций, эффективно сотрудничать,'
        ' принимать решения и реализовывать проекты через коллективный разум'
    ),
    version='0.0.1',
    contact={
        'name': 'Виталий Шаронов',
        'email': "vitaly.sharonov@gmail.com",
    },
    license_info={
        'name': 'MIT'
    },
    root_path='/api/v1',
    debug=config.PRODUCTION_MODE,
)

origins = [
    f'http://{HOST}:{PORT}',
    f'http://{HOST}:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Auth
app.include_router(auth_router, prefix='/auth', tags=['auth'])
# Filestorage
app.include_router(file_router, prefix='/file', tags=['filestorage'])
# Entities
for router_param in get_entities_routers():
    app.include_router(router_param.router, prefix=router_param.prefix, tags=router_param.tags)


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
