import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import auth_router
from core.config import HOST, PORT
from datastorage.utils import get_entities_routers

app = FastAPI(title='Self-organization API')

origins = [
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
# Entities
for router_param in get_entities_routers():
    app.include_router(router_param.router, prefix=router_param.prefix, tags=router_param.tags)

# business logic


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
