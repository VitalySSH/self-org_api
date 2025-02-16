from typing import List, TypedDict


class MyMemberRequest(TypedDict):
    key: str
    communityName: str
    communityDescription: str
    communityId: str
    status: str
    statusCode: str
    reason: str
    created: str
    solution: str
    children: List['MyMemberRequest']
