from enum import Enum


class InteractionType(str, Enum):
    SUGGESTION = "suggestion"
    CRITICISM = "criticism"
    COMBINATION = "combination"


class UserResponse(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"
