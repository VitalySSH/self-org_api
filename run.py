import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from crud.database.tables import *
from core.config import HOST, PORT
from crud.database.base import database, engine
from endpoints import users, persons

app = FastAPI(title='Self-organization API')
app.state.database = database
metadata.create_all(engine)


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

app.include_router(users.router, prefix='/users', tags=['users'])
app.include_router(persons.router, prefix='/persons', tags=['persons'])


@app.on_event('startup')
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database.connect()


@app.on_event('shutdown')
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database.disconnect()


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
