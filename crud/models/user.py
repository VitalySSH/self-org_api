from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, validator, constr


class User(BaseModel):
    id: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    password: Optional[constr(min_length=8)]
    created: Optional[datetime]
    is_active: Optional[bool]
