from typing import TypedDict, List

from fastapi import APIRouter


class IncludeRouter(TypedDict, total=False):
    router: APIRouter
    prefix: str
    tags: List[str]
