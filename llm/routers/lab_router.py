from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from core.config import USE_MOCK_LLM
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
from ..services.rate_limiting_service import get_rate_limiting_service
from ..services.token_calculator_service import get_token_calculator
from ..services.laboratory_service import LaboratoryService
from ..services.llm_service import LLMService
from ..services.preprocessing_service import PreprocessingService
from ..adapters.data_adapter import DataAdapter
from ..services.mock_llm_service import MockLLMService

router = APIRouter()


async def get_laboratory_service(
        session: AsyncSession = Depends(get_async_session)
) -> LaboratoryService:
    """Фабрика для создания LaboratoryService."""

    if USE_MOCK_LLM:
        llm_service = MockLLMService()
    else:
        providers = create_default_llm_providers()

        import os
        for provider in providers:
            if provider.name == "groq":
                provider.api_key = os.getenv("GROQ_API_KEY")
            elif provider.name == "together":
                provider.api_key = os.getenv("TOGETHER_API_KEY")
            elif provider.name == "huggingface":
                provider.api_key = os.getenv("HUGGINGFACE_API_KEY")

        llm_service = LLMService(providers)

    data_adapter = DataAdapter(session)
    preprocessing_service = PreprocessingService(data_adapter)
    rate_limiting_service = get_rate_limiting_service()
    token_calculator = get_token_calculator()

    return LaboratoryService(
        data_adapter,
        llm_service,
        preprocessing_service,
        rate_limiting_service,
        token_calculator
    )


# === Работа с направлениями мысли ===

@router.post("/directions/generate", response_model=DirectionsResponse)
async def generate_thinking_directions(
        request: DirectionsRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Генерация направлений мысли для новых участников с готовыми стартовыми решениями"""
    try:
        # Проверка rate limit
        allowed, seconds_remaining = service.rate_limiter.check_rate_limit(
            user_id=current_user.id,
            request_type="directions"
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Вы можете делать запрос этого типа раз в 30 минут",
                    "seconds_remaining": seconds_remaining,
                    "request_type": "directions"
                }
            )

        # Генерируем направления
        directions = await service.generate_thinking_directions(
            challenge_id=request.challenge_id,
            user_id=request.user_id
        )

        # Записываем факт запроса
        service.rate_limiter.record_request(
            user_id=current_user.id,
            request_type="directions"
        )

        # Получаем информацию о задаче для ответа
        challenge = await service.data_adapter.get_challenge(request.challenge_id)
        solutions = await service.data_adapter.get_challenge_solutions(
            request.challenge_id)

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
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации направлений: {str(e)}"
        )


# === Запросы к коллективному интеллекту ===

@router.post("/ideas/request", response_model=IdeasResponse)
async def request_collective_ideas(
        request: CollectiveRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Запрос новых идей (комбинации элементов) от коллективного интеллекта"""
    try:
        # Проверка rate limit
        allowed, seconds_remaining = service.rate_limiter.check_rate_limit(
            user_id=current_user.id,
            request_type="ideas"
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Вы можете делать запрос этого типа раз в 30 минут",
                    "seconds_remaining": seconds_remaining,
                    "request_type": "ideas"
                }
            )

        # Генерируем идеи
        result = await service.request_collective_ideas(
            solution_id=request.solution_id,
            max_ideas=request.max_items or 3
        )

        # Записываем факт запроса
        service.rate_limiter.record_request(
            user_id=current_user.id,
            request_type="ideas"
        )

        return IdeasResponse(
            interaction_id=result["interaction_id"],
            ideas=[
                CollectiveIdeaResponse(
                    idea_description=idea.idea_description,
                    combination_elements=[
                        e.get("element") for e in idea.combination_elements
                    ],
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
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запроса идей: {str(e)}"
        )


@router.post("/improvements/request", response_model=ImprovementsResponse)
async def request_improvement_suggestions(
        request: CollectiveRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Запрос предложений по улучшению решения"""
    try:
        # Проверка rate limit
        allowed, seconds_remaining = service.rate_limiter.check_rate_limit(
            user_id=current_user.id,
            request_type="improvements"
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Вы можете делать запрос этого типа раз в 30 минут",
                    "seconds_remaining": seconds_remaining,
                    "request_type": "improvements"
                }
            )

        # Генерируем предложения
        result = await service.request_improvement_suggestions(
            solution_id=request.solution_id,
            max_suggestions=request.max_items or 4
        )

        # Записываем факт запроса
        service.rate_limiter.record_request(
            user_id=current_user.id,
            request_type="improvements"
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
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запроса улучшений: {str(e)}"
        )


@router.post("/criticism/request", response_model=CriticismResponse)
async def request_solution_criticism(
        request: CollectiveRequest,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Запрос критики решения от коллективного интеллекта"""
    try:
        # Проверка rate limit
        allowed, seconds_remaining = service.rate_limiter.check_rate_limit(
            user_id=current_user.id,
            request_type="criticism"
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Вы можете делать запрос этого типа раз в 30 минут",
                    "seconds_remaining": seconds_remaining,
                    "request_type": "criticism"
                }
            )

        # Генерируем критику
        result = await service.request_solution_criticism(
            solution_id=request.solution_id,
            max_criticisms=request.max_items or 3
        )

        # Записываем факт запроса
        service.rate_limiter.record_request(
            user_id=current_user.id,
            request_type="criticism"
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
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запроса критики: {str(e)}"
        )


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
            item_responses=[item.model_dump() for item in response.item_responses]
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Взаимодействие не найдено"
            )

        return {
            "success": True,
            "interaction_id": interaction_id,
            "processed_items": len(response.item_responses),
            "message": "Ответ на взаимодействие сохранен"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки ответа: {str(e)}"
        )


@router.delete("/interaction/{interaction_id}")
async def delete_interaction(
        interaction_id: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Удаление взаимодействия"""
    try:
        await service.delete_interaction(interaction_id)
        return {"success": True, "message": "Взаимодействие удалено"}

    except CRUDNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления: {str(e)}"
        )


@router.delete("/solution/{solution_id}")
async def delete_solution(
        solution_id: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Удаление решения"""
    try:
        await service.delete_solution(solution_id)
        return {"success": True, "message": "Решение удалено"}

    except CRUDNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления: {str(e)}"
        )


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
            raise HTTPException(
                status_code=403,
                detail="Нет прав доступа к решению"
            )

        integrated_text = await service.integrate_accepted_items(
            solution_id=request.solution_id,
            interaction_id=request.interaction_id,
            accepted_items=request.accepted_items,
            user_modifications=request.user_modifications
        )

        return IntegrationResponse(
            integrated_text=integrated_text,
            change_description=f"Интеграция {len(request.accepted_items)} предложений КИ"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка интеграции: {str(e)}"
        )


@router.post("/solution/version/create")
async def create_solution_version(
        request: SolutionVersionRequest,
        background_tasks: BackgroundTasks,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Создание новой версии решения (после интеграции предложений ИИ)

    Запускает предобработку в фоне
    """
    try:
        # Проверяем права доступа
        has_access = await service.validate_solution_access(
            request.solution_id,
            current_user.id
        )

        if not has_access:
            raise HTTPException(
                status_code=403,
                detail="Нет прав доступа к решению"
            )

        success = await service.create_solution_version(
            solution_id=request.solution_id,
            new_content=request.new_content,
            change_description=request.change_description,
            influenced_by_interactions=request.influenced_by_interactions
        )

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Не удалось создать версию решения"
            )

        # Запускаем предобработку в фоне
        solution = await service.data_adapter.get_solution(request.solution_id)
        challenge = await service.data_adapter.get_challenge(solution.challenge_id)

        background_tasks.add_task(
            service.preprocessing.preprocess_solution,
            solution,
            challenge
        )

        return {
            "success": True,
            "solution_id": request.solution_id,
            "message": "Новая версия решения создана, предобработка запущена"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания версии: {str(e)}"
        )


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
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения метрик: {str(e)}"
        )


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
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения метрик: {str(e)}"
        )


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
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения обзора: {str(e)}"
        )


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
            raise HTTPException(
                status_code=403,
                detail="Нет прав доступа к решению"
            )

        interactions = await service.get_pending_interactions(solution_id)

        return {
            "solution_id": solution_id,
            "pending_interactions": interactions,
            "count": len(interactions)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения взаимодействий: {str(e)}"
        )


@router.get("/rate-limit/stats")
async def get_rate_limit_stats(
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Получение статистики rate limiting (для мониторинга)"""
    try:
        stats = service.get_rate_limit_stats()
        return {
            "rate_limit_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения статистики: {str(e)}"
        )


@router.post("/solution/{solution_id}/preprocess")
async def trigger_preprocessing(
        solution_id: str,
        background_tasks: BackgroundTasks,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Ручной запуск предобработки решения

    Полезно для batch обработки существующих решений
    """
    try:
        solution = await service.data_adapter.get_solution(solution_id)
        if not solution:
            raise HTTPException(status_code=404, detail="Решение не найдено")

        challenge = await service.data_adapter.get_challenge(solution.challenge_id)

        background_tasks.add_task(
            service.preprocessing.preprocess_solution,
            solution,
            challenge
        )

        return {
            "success": True,
            "solution_id": solution_id,
            "message": "Предобработка запущена в фоне"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запуска предобработки: {str(e)}"
        )


@router.get("/health")
async def llm_service_health(
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Проверка здоровья LLM провайдеров и сервисов"""
    try:
        providers_status = []

        for provider in service.llm_service.providers:
            providers_status.append({
                "name": provider.name,
                "model": provider.model,
                "priority": provider.priority,
                "max_tokens": provider.max_tokens,
                "max_context": provider.max_context_tokens,
                "status": "configured"
            })

        return {
            "status": "healthy",
            "providers": providers_status,
            "rate_limiting": service.get_rate_limit_stats(),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/rate-limit/check/{request_type}")
async def check_rate_limit_availability(
        request_type: str,
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """Проверка доступности запроса к LLM для текущего пользователя."""
    # Валидация типа запроса
    valid_types = ["ideas", "improvements", "criticism", "directions"]
    if request_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_request_type",
                "message": f"Неверный тип запроса. Допустимые: {', '.join(valid_types)}",
                "valid_types": valid_types
            }
        )

    # Проверяем rate limit
    allowed, seconds_remaining = service.rate_limiter.check_rate_limit(
        user_id=current_user.id,
        request_type=request_type
    )

    if allowed:
        return {
            "available": True,
            "request_type": request_type,
            "message": "Запрос доступен",
            "seconds_remaining": 0
        }
    else:
        # Вычисляем читаемое время
        minutes = seconds_remaining // 60
        seconds = seconds_remaining % 60

        return {
            "available": False,
            "request_type": request_type,
            "message": f"Запрос будет доступен через {minutes} минут {seconds} секунд",
            "seconds_remaining": seconds_remaining,
            "minutes_remaining": minutes,
            "formatted_time": f"{minutes}:{seconds:02d}"
        }


@router.get("/rate-limit/check-all")
async def check_all_rate_limits(
        current_user=Depends(auth_service.get_current_user),
        service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Проверка доступности всех типов запросов к LLM для текущего пользователя

    Returns:
        Статус доступности для каждого типа запроса
    """
    request_types = ["ideas", "improvements", "criticism", "directions"]
    results = {}

    for request_type in request_types:
        allowed, seconds_remaining = service.rate_limiter.check_rate_limit(
            user_id=current_user.id,
            request_type=request_type
        )

        if allowed:
            results[request_type] = {
                "available": True,
                "seconds_remaining": 0,
                "message": "Доступен"
            }
        else:
            minutes = seconds_remaining // 60
            seconds = seconds_remaining % 60

            results[request_type] = {
                "available": False,
                "seconds_remaining": seconds_remaining,
                "minutes_remaining": minutes,
                "formatted_time": f"{minutes}:{seconds:02d}",
                "message": f"Доступен через {minutes}м {seconds}с"
            }

    return {
        "user_id": current_user.id,
        "request_types": results,
        "timestamp": datetime.now().isoformat()
    }
