from dataclasses import dataclass
from typing import List

from fastapi import APIRouter

from datastorage.interfaces import InitiativeCategory


@dataclass
class RouterParams:
    prefix: str
    tags: List[str]
    router: APIRouter


@dataclass
class OtherCommunitySettings:
    categories: List[InitiativeCategory]
    is_secret_ballot: bool
    is_can_offer: bool
