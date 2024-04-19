from enum import Enum


class SessionAction(Enum):
    INVALIDATE_START = 'invalidate_start'
    INVALIDATE = 'invalidate'
    CLOSE = 'close'
