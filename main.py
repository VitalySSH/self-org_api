import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from auth.models import User
from auth.router import get_auth_router_data, get_register_router_data, fastapi_users
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

current_user = fastapi_users.current_user()


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.first_name}"


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
