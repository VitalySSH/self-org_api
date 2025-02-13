from dataclasses import dataclass


@dataclass
class CreateUserResult:
    status_code: int
    message: str
