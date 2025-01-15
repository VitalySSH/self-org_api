import abc

from core.dataclasses import BaseVotingParams


class AO(abc.ABC):

    @abc.abstractmethod
    async def calculate_voting_params(self, community_id: str) -> BaseVotingParams:
        raise NotImplementedError
