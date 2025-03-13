from dataclasses import dataclass


@dataclass(kw_only=True)
class CreateUserResult:
    status_code: int
    message: str
