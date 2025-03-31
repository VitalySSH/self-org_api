from typing import List, TypedDict, Optional


class MyMemberRequest(TypedDict):
    key: str
    communityName: str
    communityDescription: str
    communityId: str
    status: str
    statusCode: str
    reason: Optional[str]
    created: str
    children: List['MyMemberRequest']
