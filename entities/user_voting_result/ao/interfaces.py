from typing import Union, Literal

from entities.initiative.model import Initiative
from entities.rule.model import Rule

Resource = Union[Rule, Initiative]
ResourceType = Literal['rule', 'initiative']
