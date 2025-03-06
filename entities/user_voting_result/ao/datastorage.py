from datastorage.ao.datastorage import AODataStorage
from datastorage.decorators import ds_async_with_new_session
from entities.user_voting_result.model import UserVotingResult
from datastorage.crud.datastorage import CRUDDataStorage


class UserVotingResultDS(
    AODataStorage[UserVotingResult],
    CRUDDataStorage[UserVotingResult]
):

    _model = UserVotingResult

    @ds_async_with_new_session
    async def recount_vote(self, result_id: str) -> None:
        """Пересчитает результаты голосования."""
        await self.vote_count(result_id)
