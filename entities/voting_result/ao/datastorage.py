import logging

from sqlalchemy import select, func, case

from datastorage.ao.base import AODataStorage
from datastorage.crud.datastorage import CRUDDataStorage
from entities.user_voting_result.model import UserVotingResult
from entities.voting_result.ao.dataclasses import SimpleVoteResult
from entities.voting_result.model import VotingResult

logger = logging.getLogger(__name__)


class VotingResultDS(AODataStorage[VotingResult], CRUDDataStorage):
    _model = VotingResult

    async def get_vote_in_percent(self, result_id: str) -> SimpleVoteResult:
        """Вернёт статистику по простому голосованию."""
        total_count_query = select(func.count()).where(
            UserVotingResult.voting_result_id == result_id,
            UserVotingResult.is_blocked.isnot(True),
        )
        total_count_result = await self._session.execute(total_count_query)
        total_count = total_count_result.scalar()

        if total_count == 0:
            return SimpleVoteResult(yes=0, no=0, abstain=0)

        vote_counts_query = select(
            func.count(case((UserVotingResult.vote.is_(None), 1))),
            func.count(case((UserVotingResult.vote.is_(True), 1))),
            func.count(case((UserVotingResult.vote.is_(False), 1))),
        ).where(
            UserVotingResult.voting_result_id == result_id,
            UserVotingResult.is_blocked.isnot(True),
        )

        vote_counts_result = await self._session.execute(vote_counts_query)
        none_count, true_count, false_count = vote_counts_result.fetchone()

        abstain = (none_count / total_count) * 100
        yes = (true_count / total_count) * 100
        no = (false_count / total_count) * 100

        return SimpleVoteResult(yes=int(yes), no=int(no), abstain=int(abstain))
