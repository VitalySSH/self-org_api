import logging
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import auth_router
from core import config
from core.config import HOST, PORT, FRONT_HOST, FRONT_PORT
from core.lifespan import lifespan
from datastorage.utils import get_entities_routers
from filestorage.router import file_router
from scheduler.router import router as scheduler_router
from llm.routers.lab_router import router as llm_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    debug=not config.PRODUCTION_MODE,
    lifespan=lifespan,
)

front = (
    f'http://{FRONT_HOST}:{FRONT_PORT}' if
    FRONT_PORT else f'http://{FRONT_HOST}'
)
origins = [
    front,
    f'http://{HOST}:{PORT}',
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

# Scheduler (для управления задачами)
app.include_router(scheduler_router, prefix='/scheduler', tags=['scheduler'])
#LLM
app.include_router(llm_router, prefix='/llm', tags=['LLM', 'lab'])


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
