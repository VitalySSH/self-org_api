from typing import Optional

from sqlalchemy import text, select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from core.dataclasses import BaseVotingParams, SimpleVoteResult
from datastorage.ao.interfaces import AO
from datastorage.base import DataStorage
from datastorage.interfaces import T
from entities.status.model import Status
from entities.user_voting_result.model import UserVotingResult


class AODataStorage(DataStorage[T], AO):
    """Дополнительная бизнес-логика для модели."""

    def __init__(self, session: Optional[AsyncSession] = None):
        super().__init__(model=self.__class__._model, session=session)

    async def calculate_voting_params(
            self, community_id: str) -> BaseVotingParams:
        """Вычислит основные параметры голосований
        для сообщества на текущий момент."""
        query = text("""
            WITH sorted_data AS (
                SELECT 
                    quorum,
                    vote,
                    significant_minority,
                    ROW_NUMBER() OVER (PARTITION BY community_id ORDER BY quorum) AS row_num_quorum,
                    ROW_NUMBER() OVER (PARTITION BY community_id ORDER BY vote) AS row_num_vote,
                    ROW_NUMBER() OVER (PARTITION BY community_id ORDER BY significant_minority) AS row_num_minority,
                    COUNT(*) OVER (PARTITION BY community_id) AS total_count
                FROM public.user_community_settings
                WHERE community_id = :community_id AND is_blocked IS NOT TRUE
            )
            SELECT 
                ROUND(AVG(quorum)) AS quorum_median,
                ROUND(AVG(vote)) AS vote_median,
                ROUND(AVG(significant_minority)) AS minority_median
            FROM sorted_data
            WHERE 
                row_num_quorum IN ((total_count + 1) / 2, (total_count + 2) / 2)
                OR
                row_num_vote IN ((total_count + 1) / 2, (total_count + 2) / 2)
                OR
                row_num_minority IN ((total_count + 1) / 2, (total_count + 2) / 2);
        """)

        data = await self._session.execute(
            query, {'community_id': community_id})
        quorum_median, vote_median, minority_median = data.fetchone()

        return BaseVotingParams(
            vote=int(vote_median),
            quorum=int(quorum_median),
            significant_minority=int(minority_median),
        )

    async def get_status_by_code(self, code: str) -> Optional[Status]:
        """Получить статус по коду."""
        status_query = select(Status).where(Status.code == code)

        return await self._session.scalar(status_query)

    async def get_vote_in_percent(self, result_id: str) -> SimpleVoteResult:
        """Вернёт статистику по простому голосованию."""
        total_count_query = select(func.count()).where(
            UserVotingResult.voting_result_id == result_id,
            UserVotingResult.is_blocked.isnot(True),
        )
        total_count = await self._session.scalar(total_count_query)
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
