import logging

from datastorage.ao.base import AODataStorage
from datastorage.crud.datastorage import CRUDDataStorage
from entities.voting_result.model import VotingResult

logger = logging.getLogger(__name__)


class VotingResultDS(AODataStorage[VotingResult], CRUDDataStorage):
    _model = VotingResult
