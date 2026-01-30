"""
Model management API endpoints
"""
from fastapi import APIRouter, HTTPException

from api.schemas import ModelListResponse, AddModelRequest, PricingInfoResponse, ErrorResponse
from api.services.model_store import (
    get_all_models,
    add_official_model_async,
    add_custom_model_async,
)
from utils.pricing import get_model_info, format_context_window

router = APIRouter(prefix="/api", tags=["models"])


@router.get(
    "/models",
    response_model=ModelListResponse,
    summary="Get all model lists"
)
async def get_models() -> ModelListResponse:
    """
    Get both commercial and HuggingFace model lists with version number.

    The version number can be used to detect changes for caching purposes.
    """
    models = get_all_models()
    return ModelListResponse(**models)


@router.post(
    "/models",
    response_model=ModelListResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
    summary="Add a new model"
)
async def add_model(request: AddModelRequest) -> ModelListResponse:
    """
    Add a new model to the specified category.

    - **name**: Model name to add
    - **type**: Either "official" (commercial) or "custom" (HuggingFace)

    Returns the updated model list with new version number.
    """
    try:
        if request.type == "official":
            await add_official_model_async(request.name)
        else:
            await add_custom_model_async(request.name)

        models = get_all_models()
        return ModelListResponse(**models)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/pricing/{model_name:path}",
    response_model=PricingInfoResponse,
    summary="Get pricing info for a model"
)
async def get_pricing(model_name: str) -> PricingInfoResponse:
    """
    Get pricing and context window information for a model.

    - **model_name**: Model name (supports partial matching)

    Returns pricing info or null values if model not found in pricing database.
    """
    normalized = model_name.lower().strip()
    info = get_model_info(normalized)

    response = PricingInfoResponse(model=normalized)

    if info:
        response.input_price = info.get("input_price")
        response.context_window = info.get("context_window")
        if response.context_window:
            response.context_window_formatted = format_context_window(response.context_window)

    return response
