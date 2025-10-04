from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from core.config import USE_MOCK_LLM, HUGGINGFACE_API_KEY
from datastorage.crud.exceptions import CRUDNotFound
from datastorage.database.base import get_async_session
from ..models.lab import (
    DirectionsResponse, DirectionsRequest, ThinkingDirectionResponse,
    IdeasResponse, CollectiveRequest, CollectiveIdeaResponse,
    ImprovementsResponse, ImprovementSuggestionResponse, CriticismResponse,
    CriticismPointResponse, InteractionResponse, IntegrationResponse,
    IntegrationRequest, SolutionVersionRequest, AIInfluenceResponse,
    CollectiveMetricsResponse, CommunityAIOverviewResponse
)
from ..providers import create_default_llm_providers
from ..services.laboratory_service import LaboratoryService
from ..services.llm_service import LLMService
from ..adapters.data_adapter import DataAdapter
from ..services.mock_llm_service import MockLLMService

router = APIRouter()


async def get_laboratory_service(
    session: AsyncSession = Depends(get_async_session)
) -> LaboratoryService:
    """Создание сервиса лаборатории с зависимостями"""

    if USE_MOCK_LLM:
        llm_service = MockLLMService()
    else:
        providers = create_default_llm_providers()
    
        # Устанавливаем API ключи из переменных окружения
        import os
        for provider in providers:
            if provider.name == "huggingface":
                provider.api_key = HUGGINGFACE_API_KEY
            # elif provider.name == "anthropic":
            #     provider.api_key = os.getenv("ANTHROPIC_API_KEY")
            # elif provider.name == "openai":
            #     provider.api_key = os.getenv("OPENAI_API_KEY")

        llm_service = LLMService(providers)

    data_adapter = DataAdapter(session)

    return LaboratoryService(data_adapter, llm_service)


# === Работа с направлениями мысли ===

@router.post("/directions/generate", response_model=DirectionsResponse)
async def generate_thinking_directions(
        request: DirectionsRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Генерация направлений мысли для новых участников с готовыми стартовыми решениями"""
    try:
        directions = await service.generate_thinking_directions(
            challenge_id=request.challenge_id,
            user_id=request.user_id
        )

        # Получаем информацию о задаче для ответа
        challenge = await service.data_adapter.get_challenge(
            request.challenge_id
        )
        solutions = await service.data_adapter.get_challenge_solutions(
            request.challenge_id
        )

        return DirectionsResponse(
            directions=[
                ThinkingDirectionResponse(**direction.dict())
                for direction in directions
            ],
            total_participants=len(solutions),
            challenge_title=challenge.title if challenge else "Неизвестная задача"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка генерации направлений: {str(e)}")


# === Запросы к коллективному интеллекту ===

@router.post("/ideas/request", response_model=IdeasResponse)
async def request_collective_ideas(
        request: CollectiveRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Запрос новых идей (комбинации элементов) от коллективного интеллекта"""
    try:
        result = await service.request_collective_ideas(
            solution_id=request.solution_id,
            max_ideas=request.max_items or 3
        )

        return IdeasResponse(
            interaction_id=result["interaction_id"],
            ideas=[
                CollectiveIdeaResponse(
                    idea_description=idea.idea_description,
                    combination_elements=[e.get("element") for e in idea.combination_elements],
                    source_solutions_count=idea.source_solutions_count,
                    potential_impact=idea.potential_impact,
                    reasoning=idea.reasoning,
                )
                for idea in result["ideas"]
            ],
            total_count=result["total_count"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка запроса идей: {str(e)}")


@router.post("/improvements/request", response_model=ImprovementsResponse)
async def request_improvement_suggestions(
        request: CollectiveRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Запрос предложений по улучшению решения"""
    try:
        result = await service.request_improvement_suggestions(
            solution_id=request.solution_id,
            max_suggestions=request.max_items or 4
        )

        return ImprovementsResponse(
            interaction_id=result["interaction_id"],
            suggestions=[
                ImprovementSuggestionResponse(**suggestion.dict())
                for suggestion in result["suggestions"]
            ],
            total_count=result["total_count"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка запроса улучшений: {str(e)}")


@router.post("/criticism/request", response_model=CriticismResponse)
async def request_solution_criticism(
        request: CollectiveRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Запрос критики решения от коллективного интеллекта"""
    try:
        result = await service.request_solution_criticism(
            solution_id=request.solution_id,
            max_criticisms=request.max_items or 3
        )

        return CriticismResponse(
            interaction_id=result["interaction_id"],
            criticisms=[
                CriticismPointResponse(**criticism.dict())
                for criticism in result["criticisms"]
            ],
            total_count=result["total_count"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка запроса критики: {str(e)}")


# === Обработка ответов пользователя ===

@router.post("/interaction/{interaction_id}/respond")
async def respond_to_interaction(
        interaction_id: str,
        response: InteractionResponse,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Ответ пользователя на предложения ИИ (Принять/Отклонить/Изменить)"""
    try:
        success = await service.respond_to_interaction(
            interaction_id=interaction_id,
            item_responses=[
                item.model_dump() for item in response.item_responses
            ]
        )

        if not success:
            raise HTTPException(status_code=404,
                                detail="Взаимодействие не найдено")

        return {
            "success": True,
            "interaction_id": interaction_id,
            "processed_items": len(response.item_responses),
            "message": "Ответ на взаимодействие сохранен"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка обработки ответа: {str(e)}")

@router.delete("/interaction/{interaction_id}")
async def delete_interaction(
        interaction_id: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    try:
        await service.delete_interaction(interaction_id)

    except CRUDNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка обработки ответа: {str(e)}")


@router.delete("/solution/{solution_id}")
async def delete_solution(
        solution_id: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    try:
        await service.delete_solution(solution_id)

    except CRUDNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка обработки ответа: {str(e)}")


@router.post("/integration/apply", response_model=IntegrationResponse)
async def apply_integration(
        request: IntegrationRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Интеграция принятых предложений в решение с помощью ИИ"""
    try:
        # Проверяем права доступа к решению
        has_access = await service.validate_solution_access(
            request.solution_id,
            current_user.id
        )

        if not has_access:
            raise HTTPException(status_code=403,
                                detail="Нет прав доступа к решению")

        integrated_text = await service.integrate_accepted_items(
            solution_id=request.solution_id,
            interaction_id=request.interaction_id,
            accepted_items=request.accepted_items,
            user_modifications=request.user_modifications
        )

        return IntegrationResponse(
            integrated_text=integrated_text,
            change_description=f"Интеграция {len(request.accepted_items)} предложений KИ"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка интеграции: {str(e)}")


@router.post("/solution/version/create")
async def create_solution_version(
        request: SolutionVersionRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Создание новой версии решения (после интеграции предложений ИИ)"""
    try:
        # Проверяем права доступа
        has_access = await service.validate_solution_access(
            request.solution_id,
            current_user.id
        )

        if not has_access:
            raise HTTPException(status_code=403,
                                detail="Нет прав доступа к решению")

        success = await service.create_solution_version(
            solution_id=request.solution_id,
            new_content=request.new_content,
            change_description=request.change_description,
            influenced_by_interactions=request.influenced_by_interactions
        )

        if not success:
            raise HTTPException(status_code=400,
                                detail="Не удалось создать версию решения")

        return {
            "success": True,
            "solution_id": request.solution_id,
            "message": "Новая версия решения создана"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка создания версии: {str(e)}")


# === Аналитика и метрики ИИ ===

@router.get(
    "/analytics/solution-ai-influence/{solution_id}",
    response_model=AIInfluenceResponse
)
async def get_solution_ai_influence(
        solution_id: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Получение метрик влияния ИИ на конкретное решение"""
    try:
        influence_data = await service.get_solution_ai_influence(solution_id)

        return AIInfluenceResponse(**influence_data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка получения метрик: {str(e)}")


@router.get(
    "/analytics/collective-metrics/{challenge_id}",
    response_model=CollectiveMetricsResponse
)
async def get_collective_metrics(
        challenge_id: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Получение метрик коллективного интеллекта для задачи"""
    try:
        metrics = await service.get_collective_metrics(challenge_id)

        return CollectiveMetricsResponse(**metrics)

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка получения метрик: {str(e)}")


@router.get(
    "/analytics/community-ai-overview/{community_id}",
    response_model=CommunityAIOverviewResponse
)
async def get_community_ai_overview(
        community_id: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Обзор использования ИИ в сообществе"""
    try:
        overview = await service.get_community_ai_overview(community_id)

        return CommunityAIOverviewResponse(**overview)

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка получения обзора: {str(e)}")


# === Вспомогательные эндпоинты ===

@router.get("/solution/{solution_id}/pending-interactions")
async def get_pending_interactions(
        solution_id: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Получение ожидающих ответа взаимодействий с ИИ для решения"""
    try:
        # Проверяем права доступа
        has_access = await service.validate_solution_access(
            solution_id,
            current_user.id
        )

        if not has_access:
            raise HTTPException(status_code=403,
                                detail="Нет прав доступа к решению")

        interactions = await service.get_pending_interactions(solution_id)

        return {
            "solution_id": solution_id,
            "pending_interactions": interactions,
            "count": len(interactions)
        }

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка получения взаимодействий: {str(e)}")


@router.get("/health")
async def llm_service_health(
    service: LaboratoryService = Depends(get_laboratory_service)
):
    try:
        providers_status = []

        for provider in service.llm_service.providers:
            if provider.name == "huggingface":
                status = await service.llm_service.check_huggingface_health(
                    provider
                )
            # elif provider.name == "ollama":
            #     status = await service.llm_service.check_ollama_health(
            #         provider
            #     )
            else:
                status = {"status": "unknown", "error": "Unsupported provider"}

            providers_status.append({
                "name": provider.name,
                **status
            })

        all_healthy = all(p["status"] == "healthy" for p in providers_status)

        return {
            "status": "healthy" if all_healthy else "degraded",
            "providers": providers_status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
