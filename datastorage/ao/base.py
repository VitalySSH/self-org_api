from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.dataclasses import BaseVotingParams
from datastorage.ao.interfaces import AO
from datastorage.base import DataStorage
from datastorage.interfaces import T


class AODataStorage(DataStorage[T], AO):
    """Дополнительная бизнес-логика для модели."""

    def __init__(self, session: Optional[AsyncSession] = None):
        super().__init__(model=self.__class__._model, session=session)

    async def calculate_voting_params(self, community_id: str) -> BaseVotingParams:
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

        data = await self._session.execute(query, {'community_id': community_id})
        quorum_median, vote_median, minority_median = data.fetchone()

        return BaseVotingParams(
            vote=int(vote_median),
            quorum=int(quorum_median),
            significant_minority=int(minority_median),
        )
