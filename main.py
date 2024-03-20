import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import auth_router
from business_logic.routers.voting import voting_router
from core.config import HOST, PORT
from datastorage.crud.entities.community.routers import community_router
from datastorage.crud.entities.community_settings.routers import cs_router
from datastorage.crud.entities.initiative_category.routers import ic_router
from datastorage.crud.entities.status.routers import status_router
from datastorage.crud.entities.user.routers import user_router

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

# CRUD and Auth
app.include_router(auth_router, prefix='/auth', tags=['auth'])
app.include_router(user_router, prefix='/user', tags=['user'])
app.include_router(cs_router, prefix='/community_settings', tags=['community_settings'])
app.include_router(community_router, prefix='/community', tags=['community'])
app.include_router(status_router, prefix='/status', tags=['status'])
app.include_router(ic_router, prefix='/initiative_category', tags=['initiative_category'])
# business logic
app.include_router(voting_router, prefix='/voting', tags=['voting'])


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
