from enum import Enum


class SolutionStatus(str, Enum):
    DRAFT = "draft"
    READY_FOR_REVIEW = "ready_for_review"
    COMPLETED = "completed"
