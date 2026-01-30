"""
Token counting API endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional

from api.schemas import TokenCountRequest, TokenCountResponse, ErrorResponse
from api.schemas.models import ModelType
from api.services.token_counter import (
    count_tokens_for_model,
    APIKeyMissingError,
    UnsupportedModelError,
)
from api.services.file_parser import (
    parse_uploaded_file,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from api.services.model_store import (
    add_official_model_async,
    add_custom_model_async,
)

router = APIRouter(prefix="/api", tags=["tokens"])


@router.post(
    "/count-tokens",
    response_model=TokenCountResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "API key missing"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    }
)
async def count_tokens(request: TokenCountRequest) -> TokenCountResponse:
    """
    Count tokens for the given text using the specified model.

    - **text**: The text to count tokens for
    - **model**: Model name (e.g., gpt-4o, claude-3-5-sonnet, meta-llama/llama-4)
    - **model_type**: Either "commercial" or "huggingface"
    """
    try:
        is_commercial = request.model_type == ModelType.COMMERCIAL

        result = count_tokens_for_model(
            model_name=request.model,
            text=request.text,
            is_commercial=is_commercial
        )

        # Add model to store if successful
        if is_commercial:
            await add_official_model_async(request.model)
        else:
            await add_custom_model_async(request.model)

        return TokenCountResponse(**result)

    except APIKeyMissingError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except UnsupportedModelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/count-tokens/file",
    response_model=TokenCountResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "API key missing"},
        413: {"model": ErrorResponse, "description": "File too large"},
        415: {"model": ErrorResponse, "description": "Unsupported file type"},
    }
)
async def count_tokens_file(
    file: UploadFile = File(..., description="File to count tokens for"),
    model: str = Form(..., min_length=2, description="Model name"),
    model_type: str = Form(..., description="Model type: commercial or huggingface")
) -> TokenCountResponse:
    """
    Count tokens for an uploaded file using the specified model.

    Supported file types: .pdf, .docx, .txt, .md

    - **file**: The file to count tokens for
    - **model**: Model name (e.g., gpt-4o, claude-3-5-sonnet, meta-llama/llama-4)
    - **model_type**: Either "commercial" or "huggingface"
    """
    try:
        # Parse model type
        try:
            model_type_enum = ModelType(model_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model_type: {model_type}. Must be 'commercial' or 'huggingface'"
            )

        is_commercial = model_type_enum == ModelType.COMMERCIAL

        # Parse file content
        text = await parse_uploaded_file(file.file, file.filename)

        # Count tokens
        result = count_tokens_for_model(
            model_name=model,
            text=text,
            is_commercial=is_commercial
        )

        # Add model to store if successful
        if is_commercial:
            await add_official_model_async(model)
        else:
            await add_custom_model_async(model)

        return TokenCountResponse(**result)

    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except APIKeyMissingError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except UnsupportedModelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
