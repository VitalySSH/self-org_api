from typing import List

from endpoints.base import BaseRouter


class UserRouter(BaseRouter):

    async def list(self, filters: List[dict]):
        return

    async def get(self, id: str):
        return

    async def create(self):
        return

    async def update(self):
        return

    async def get_by_email(self, email: str):
        return

    async def get_by_phone(self, phone: str):
        return
