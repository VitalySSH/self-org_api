import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import get_auth_router_data, get_register_router_data, get_user_router_data, \
    user_router
from core.config import HOST, PORT


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


app.include_router(**get_auth_router_data())
app.include_router(**get_register_router_data())
app.include_router(**get_user_router_data())
app.include_router(user_router, prefix='/users', tags=['users'])


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
