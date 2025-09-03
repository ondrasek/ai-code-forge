"""Pydantic schema definitions for structured outputs.

This module defines the schema models used for structured outputs
with OpenAI's JSON Schema validation features.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority levels for tasks and issues."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Sentiment(str, Enum):
    """Sentiment analysis values."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class DataExtraction(BaseModel):
    """Structured data extraction from unstructured text."""
    model_config = ConfigDict(extra="forbid")
    
    entities: List[str] = Field(
        description="List of named entities found in the text",
        examples=[["OpenAI", "Python", "JSON Schema"]]
    )
    key_facts: List[str] = Field(
        description="Important facts or statements extracted from the text",
        min_length=1,
        max_length=10
    )
    summary: str = Field(
        description="Brief summary of the main content",
        min_length=10,
        max_length=500
    )
    confidence_score: float = Field(
        description="Confidence in the extraction accuracy (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )


class CodeAnalysis(BaseModel):
    """Structured code analysis results."""
    model_config = ConfigDict(extra="forbid")
    
    language: str = Field(
        description="Programming language detected",
        examples=["python", "javascript", "typescript", "rust"]
    )
    complexity_score: int = Field(
        description="Code complexity score (1-10, where 10 is most complex)",
        ge=1,
        le=10
    )
    issues: List[str] = Field(
        description="List of potential issues or improvements identified",
        default=[]
    )
    strengths: List[str] = Field(
        description="Positive aspects of the code",
        default=[]
    )
    recommendations: List[str] = Field(
        description="Specific recommendations for improvement",
        default=[]
    )
    functions_count: int = Field(
        description="Number of functions or methods identified",
        ge=0
    )
    lines_of_code: int = Field(
        description="Approximate lines of code (excluding comments and blank lines)",
        ge=0
    )


class ConfigurationTask(BaseModel):
    """Structured configuration task definition."""
    model_config = ConfigDict(extra="forbid")
    
    task_name: str = Field(
        description="Descriptive name for the configuration task",
        min_length=3,
        max_length=100
    )
    priority: PriorityLevel = Field(
        description="Priority level of this task"
    )
    steps: List[str] = Field(
        description="Ordered list of steps to complete the task",
        min_length=1,
        max_length=20
    )
    prerequisites: List[str] = Field(
        description="Required prerequisites before starting this task",
        default=[]
    )
    estimated_duration: str = Field(
        description="Estimated time to complete (e.g., '30 minutes', '2 hours')",
        pattern=r'^\d+\s+(minutes?|hours?|days?)$'
    )
    validation_criteria: List[str] = Field(
        description="Criteria to validate successful completion",
        min_length=1
    )


class SentimentAnalysis(BaseModel):
    """Structured sentiment analysis results."""
    model_config = ConfigDict(extra="forbid")
    
    overall_sentiment: Sentiment = Field(
        description="Overall sentiment classification"
    )
    confidence: float = Field(
        description="Confidence in sentiment analysis (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    key_phrases: List[str] = Field(
        description="Key phrases that influenced the sentiment analysis",
        max_length=10
    )
    emotions: Dict[str, float] = Field(
        description="Emotion scores (joy, anger, fear, surprise, etc.) from 0.0 to 1.0",
        default={}
    )
    reasoning: str = Field(
        description="Brief explanation of why this sentiment was assigned",
        min_length=20,
        max_length=300
    )


class APIResponseFormat(BaseModel):
    """Generic API response format with structured data."""
    model_config = ConfigDict(extra="forbid")
    
    success: bool = Field(
        description="Whether the operation was successful"
    )
    data: Union[DataExtraction, CodeAnalysis, ConfigurationTask, SentimentAnalysis] = Field(
        description="The structured data payload"
    )
    metadata: Dict[str, Any] = Field(
        description="Additional metadata about the operation",
        default={}
    )
    timestamp: str = Field(
        description="ISO timestamp of when the response was generated",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    )
    processing_time_ms: float = Field(
        description="Time taken to process the request in milliseconds",
        ge=0.0
    )


class ValidationError(BaseModel):
    """Structured validation error information."""
    model_config = ConfigDict(extra="forbid")
    
    field: str = Field(
        description="Field name where validation failed"
    )
    message: str = Field(
        description="Human-readable error message"
    )
    expected_type: str = Field(
        description="Expected data type or format"
    )
    received_value: Optional[str] = Field(
        description="The value that failed validation (truncated if too long)",
        default=None
    )


class ErrorResponse(BaseModel):
    """Structured error response format."""
    model_config = ConfigDict(extra="forbid")
    
    success: bool = Field(
        description="Always false for error responses",
        default=False
    )
    error_type: str = Field(
        description="Type of error (validation, api, processing, etc.)"
    )
    error_message: str = Field(
        description="Human-readable error description"
    )
    validation_errors: List[ValidationError] = Field(
        description="Detailed validation errors if applicable",
        default=[]
    )
    timestamp: str = Field(
        description="ISO timestamp of when the error occurred"
    )


# Schema registry for easy access
SCHEMA_REGISTRY = {
    "data_extraction": DataExtraction,
    "code_analysis": CodeAnalysis,
    "configuration_task": ConfigurationTask,
    "sentiment_analysis": SentimentAnalysis,
    "api_response": APIResponseFormat,
    "error_response": ErrorResponse
}


def get_json_schema(schema_name: str) -> Dict[str, Any]:
    """Get JSON schema for a given schema name.
    
    Args:
        schema_name: Name of the schema from SCHEMA_REGISTRY
        
    Returns:
        JSON schema dictionary
        
    Raises:
        KeyError: If schema_name is not found in registry
    """
    if schema_name not in SCHEMA_REGISTRY:
        raise KeyError(f"Schema '{schema_name}' not found. Available: {list(SCHEMA_REGISTRY.keys())}")
    
    return SCHEMA_REGISTRY[schema_name].model_json_schema()


def validate_structured_data(data: Dict[str, Any], schema_name: str) -> Union[BaseModel, List[ValidationError]]:
    """Validate data against a schema.
    
    Args:
        data: Data to validate
        schema_name: Name of the schema from SCHEMA_REGISTRY
        
    Returns:
        Validated Pydantic model instance or list of validation errors
    """
    if schema_name not in SCHEMA_REGISTRY:
        return [ValidationError(
            field="schema_name",
            message=f"Schema '{schema_name}' not found",
            expected_type="valid schema name",
            received_value=schema_name
        )]
    
    schema_class = SCHEMA_REGISTRY[schema_name]
    
    try:
        return schema_class.model_validate(data)
    except Exception as e:
        # Convert Pydantic validation errors to our structured format
        errors = []
        if hasattr(e, 'errors'):
            for error in e.errors():
                field_path = ".".join(str(loc) for loc in error.get('loc', []))
                errors.append(ValidationError(
                    field=field_path,
                    message=error.get('msg', 'Validation failed'),
                    expected_type=error.get('type', 'unknown'),
                    received_value=str(error.get('input', ''))[:100]  # Truncate long values
                ))
        else:
            errors.append(ValidationError(
                field="unknown",
                message=str(e),
                expected_type="valid data",
                received_value=str(data)[:100]
            ))
        
        return errors