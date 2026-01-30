"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum


class ModelType(str, Enum):
    COMMERCIAL = "commercial"
    HUGGINGFACE = "huggingface"


class TokenCountRequest(BaseModel):
    """Request schema for token counting"""
    text: str = Field(..., min_length=1, description="Text to count tokens for")
    model: str = Field(..., min_length=2, description="Model name")
    model_type: ModelType = Field(..., description="Type of model (commercial or huggingface)")


class TokenCountResponse(BaseModel):
    """Response schema for token counting"""
    token_count: int = Field(..., ge=0, description="Number of tokens")
    cost_usd: Optional[float] = Field(None, description="Estimated cost in USD")
    context_window: Optional[int] = Field(None, description="Model's context window size")
    context_usage_percent: Optional[float] = Field(None, description="Percentage of context window used")
    model: str = Field(..., description="Model name used for counting")


class ModelListResponse(BaseModel):
    """Response schema for model list"""
    official: list[str] = Field(default_factory=list, description="Commercial model list")
    custom: list[str] = Field(default_factory=list, description="HuggingFace model list")
    version: int = Field(..., description="Version number for change tracking")


class AddModelRequest(BaseModel):
    """Request schema for adding a new model"""
    name: str = Field(..., min_length=2, description="Model name to add")
    type: Literal["official", "custom"] = Field(..., description="Model category")


class PricingInfoResponse(BaseModel):
    """Response schema for pricing information"""
    model: str = Field(..., description="Model name")
    input_price: Optional[float] = Field(None, description="Price per 1M input tokens in USD")
    context_window: Optional[int] = Field(None, description="Context window size")
    context_window_formatted: Optional[str] = Field(None, description="Formatted context window (e.g., '128K')")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")


class WebSocketMessageType(str, Enum):
    INIT = "init"
    MODEL_ADDED = "model_added"
    ADD_MODEL = "add_model"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    """WebSocket message schema"""
    type: WebSocketMessageType = Field(..., description="Message type")
    data: Optional[dict] = Field(None, description="Message data")
    error: Optional[str] = Field(None, description="Error message if type is error")
