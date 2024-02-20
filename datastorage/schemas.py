from pydantic import BaseModel


class GetByIdSchema(BaseModel):
    id: str
