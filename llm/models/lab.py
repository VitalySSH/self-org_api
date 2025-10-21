from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from llm.interfaces.lab import CombinationElement


class LLMProvider(BaseModel):
    """Конфигурация провайдера LLM"""
    name: str
    api_url: str
    api_key: Optional[str] = None
    model: str
    max_tokens: int = 4000
    max_context_tokens: int = 4096
    safe_usage_ratio: float = 0.8
    temperature: float = 0.7
    timeout: int = 30
    priority: int = 1


class ThinkingDirection(BaseModel):
    """Направление мысли с готовым стартовым решением"""
    title: str
    description: str
    key_approaches: List[str]
    participants_count: int
    initial_solution_text: str
    example_excerpts: List[str]


class CollectiveIdea(BaseModel):
    """Идея от коллективного интеллекта"""
    idea_description: str
    combination_elements: List[CombinationElement]
    source_solutions_count: int
    potential_impact: str
    reasoning: str


class ImprovementSuggestion(BaseModel):
    """Предложение по улучшению"""
    target_element: str
    improvement_description: str
    integration_advice: str
    source_examples: List[str]
    reasoning: str


class CriticismPoint(BaseModel):
    """Критическое замечание"""
    criticism_text: str
    severity: str  # minor, major, critical
    evidence: List[str]
    suggested_fix: str
    reasoning: str


class DirectionsRequest(BaseModel):
    challenge_id: str
    user_id: str


class ThinkingDirectionResponse(BaseModel):
    title: str
    description: str
    key_approaches: List[str]
    participants_count: int
    initial_solution_text: str
    example_excerpts: List[str]


class DirectionsResponse(BaseModel):
    directions: List[ThinkingDirectionResponse]
    total_participants: int
    challenge_title: str


class CollectiveRequest(BaseModel):
    solution_id: str
    max_items: Optional[int] = 3


class CollectiveIdeaResponse(BaseModel):
    idea_description: str
    combination_elements: List[str]
    source_solutions_count: int
    potential_impact: str
    reasoning: str


class IdeasResponse(BaseModel):
    interaction_id: str
    ideas: List[CollectiveIdeaResponse]
    total_count: int


class ImprovementSuggestionResponse(BaseModel):
    target_element: str
    improvement_description: str
    integration_advice: str
    source_examples: List[str]
    reasoning: str


class ImprovementsResponse(BaseModel):
    interaction_id: str
    suggestions: List[ImprovementSuggestionResponse]
    total_count: int


class CriticismPointResponse(BaseModel):
    criticism_text: str
    severity: str
    evidence: List[str]
    suggested_fix: str
    reasoning: str


class CriticismResponse(BaseModel):
    interaction_id: str
    criticisms: List[CriticismPointResponse]
    total_count: int


class ItemResponse(BaseModel):
    item_index: int
    response: str = Field(..., pattern="^(accepted|rejected|modified)$")
    reasoning: Optional[str] = None
    modification: Optional[str] = None
    original_text: Optional[str] = None


class InteractionResponse(BaseModel):
    interaction_id: str
    item_responses: List[ItemResponse]


class IntegrationRequest(BaseModel):
    solution_id: str
    interaction_id: str
    accepted_items: List[Dict[str, Any]]
    user_modifications: Optional[List[str]] = None


class IntegrationResponse(BaseModel):
    integrated_text: str
    change_description: str


class SolutionVersionRequest(BaseModel):
    solution_id: str
    new_content: str
    change_description: str
    influenced_by_interactions: Optional[List[str]] = None


class AIInfluenceResponse(BaseModel):
    solution_id: str
    total_versions: int
    ai_interactions: int
    collective_influence_percentage: float
    ai_contribution_timeline: List[Dict[str, Any]]


class CollectiveMetricsResponse(BaseModel):
    challenge_id: str
    total_solutions: int
    unique_participants: int
    average_collective_influence: float
    ai_utilization_rate: float
    collaboration_intensity: str


class CommunityAIOverviewResponse(BaseModel):
    community_id: str
    total_solutions: int
    ai_assisted_solutions: int
    ai_adoption_rate: float
    total_ai_interactions: int
    average_interactions_per_solution: float
