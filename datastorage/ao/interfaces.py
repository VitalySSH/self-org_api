import abc

from core.dataclasses import BaseVotingParams


class AO(abc.ABC):

    @abc.abstractmethod
    async def calc_voting_params(self, community_id: str) -> BaseVotingParams:
        raise NotImplementedError
