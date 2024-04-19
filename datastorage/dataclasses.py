from dataclasses import dataclass
from typing import List

from fastapi import APIRouter


@dataclass
class RouterParams:
    prefix: str
    tags: List[str]
    router: APIRouter
