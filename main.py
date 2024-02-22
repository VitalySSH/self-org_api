import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.routers.auth_router import auth_router
from auth.routers.user_router import user_router
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


app.include_router(auth_router, prefix='/auth', tags=['auth'])
app.include_router(user_router, prefix='/user', tags=['user'])


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
