"""Tests for schema validation and Pydantic models."""

import pytest
import json
from datetime import datetime

from openai_structured_mcp.schemas import (
    DataExtraction,
    CodeAnalysis,
    ConfigurationTask,
    SentimentAnalysis,
    APIResponseFormat,
    ErrorResponse,
    ValidationError,
    PriorityLevel,
    Sentiment,
    get_json_schema,
    validate_structured_data,
    SCHEMA_REGISTRY
)


class TestSchemaModels:
    """Test Pydantic model validation and serialization."""
    
    def test_data_extraction_valid(self):
        """Test valid data extraction model."""
        data = {
            "entities": ["OpenAI", "Python", "API"],
            "key_facts": ["OpenAI provides API access", "Python is popular for AI"],
            "summary": "This text discusses OpenAI's API and Python integration for AI development.",
            "confidence_score": 0.95
        }
        
        model = DataExtraction.model_validate(data)
        assert model.entities == ["OpenAI", "Python", "API"]
        assert len(model.key_facts) == 2
        assert model.confidence_score == 0.95
        assert 10 <= len(model.summary) <= 500
    
    def test_data_extraction_invalid_confidence(self):
        """Test data extraction with invalid confidence score."""
        data = {
            "entities": ["Test"],
            "key_facts": ["Some fact"],
            "summary": "Valid summary text",
            "confidence_score": 1.5  # Invalid: > 1.0
        }
        
        with pytest.raises(Exception):
            DataExtraction.model_validate(data)
    
    def test_code_analysis_valid(self):
        """Test valid code analysis model."""
        data = {
            "language": "python",
            "complexity_score": 5,
            "issues": ["Missing docstrings"],
            "strengths": ["Good variable names"],
            "recommendations": ["Add type hints"],
            "functions_count": 3,
            "lines_of_code": 50
        }
        
        model = CodeAnalysis.model_validate(data)
        assert model.language == "python"
        assert 1 <= model.complexity_score <= 10
        assert model.functions_count >= 0
        assert model.lines_of_code >= 0
    
    def test_code_analysis_invalid_complexity(self):
        """Test code analysis with invalid complexity score."""
        data = {
            "language": "python",
            "complexity_score": 15,  # Invalid: > 10
            "functions_count": 3,
            "lines_of_code": 50
        }
        
        with pytest.raises(Exception):
            CodeAnalysis.model_validate(data)
    
    def test_configuration_task_valid(self):
        """Test valid configuration task model."""
        data = {
            "task_name": "Setup Development Environment",
            "priority": "high",
            "steps": ["Install dependencies", "Configure settings"],
            "prerequisites": ["Admin access"],
            "estimated_duration": "2 hours",
            "validation_criteria": ["Environment works", "Tests pass"]
        }
        
        model = ConfigurationTask.model_validate(data)
        assert model.task_name == "Setup Development Environment"
        assert model.priority == PriorityLevel.HIGH
        assert len(model.steps) >= 1
        assert len(model.validation_criteria) >= 1
    
    def test_configuration_task_invalid_duration(self):
        """Test configuration task with invalid duration format."""
        data = {
            "task_name": "Test Task",
            "priority": "medium",
            "steps": ["Do something"],
            "estimated_duration": "invalid duration",  # Invalid format
            "validation_criteria": ["Task completed"]
        }
        
        with pytest.raises(Exception):
            ConfigurationTask.model_validate(data)
    
    def test_sentiment_analysis_valid(self):
        """Test valid sentiment analysis model."""
        data = {
            "overall_sentiment": "positive",
            "confidence": 0.85,
            "key_phrases": ["great experience", "highly recommend"],
            "emotions": {"joy": 0.8, "satisfaction": 0.9},
            "reasoning": "The text contains positive language and enthusiastic expressions."
        }
        
        model = SentimentAnalysis.model_validate(data)
        assert model.overall_sentiment == Sentiment.POSITIVE
        assert 0.0 <= model.confidence <= 1.0
        assert len(model.reasoning) >= 20
    
    def test_api_response_format_valid(self):
        """Test valid API response format."""
        data_extraction = {
            "entities": ["Test"],
            "key_facts": ["Fact"],
            "summary": "Test summary",
            "confidence_score": 0.8
        }
        
        response_data = {
            "success": True,
            "data": data_extraction,
            "metadata": {"source": "test"},
            "timestamp": "2024-01-01T12:00:00",
            "processing_time_ms": 150.5
        }
        
        model = APIResponseFormat.model_validate(response_data)
        assert model.success is True
        assert isinstance(model.data, DataExtraction)
        assert model.processing_time_ms >= 0.0
    
    def test_error_response_valid(self):
        """Test valid error response format."""
        validation_error = {
            "field": "temperature",
            "message": "Value must be between 0.0 and 2.0",
            "expected_type": "float",
            "received_value": "3.5"
        }
        
        error_data = {
            "error_type": "validation",
            "error_message": "Input validation failed",
            "validation_errors": [validation_error],
            "timestamp": "2024-01-01T12:00:00"
        }
        
        model = ErrorResponse.model_validate(error_data)
        assert model.success is False  # Default value
        assert model.error_type == "validation"
        assert len(model.validation_errors) == 1
        assert isinstance(model.validation_errors[0], ValidationError)


class TestSchemaUtilities:
    """Test schema utility functions."""
    
    def test_get_json_schema_valid(self):
        """Test getting JSON schema for valid schema name."""
        schema = get_json_schema("data_extraction")
        
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "entities" in schema["properties"]
        assert "key_facts" in schema["properties"]
        assert "summary" in schema["properties"]
        assert "confidence_score" in schema["properties"]
    
    def test_get_json_schema_invalid(self):
        """Test getting JSON schema for invalid schema name."""
        with pytest.raises(KeyError) as exc_info:
            get_json_schema("invalid_schema")
        
        assert "Schema 'invalid_schema' not found" in str(exc_info.value)
        assert "data_extraction" in str(exc_info.value)  # Should list available schemas
    
    def test_validate_structured_data_valid(self):
        """Test validating valid structured data."""
        data = {
            "entities": ["Test"],
            "key_facts": ["Some fact"],
            "summary": "Valid summary text",
            "confidence_score": 0.9
        }
        
        result = validate_structured_data(data, "data_extraction")
        assert isinstance(result, DataExtraction)
        assert result.entities == ["Test"]
        assert result.confidence_score == 0.9
    
    def test_validate_structured_data_invalid_schema(self):
        """Test validating data with invalid schema name."""
        data = {"test": "data"}
        
        result = validate_structured_data(data, "invalid_schema")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ValidationError)
        assert result[0].field == "schema_name"
        assert "Schema 'invalid_schema' not found" in result[0].message
    
    def test_validate_structured_data_validation_error(self):
        """Test validating invalid structured data."""
        data = {
            "entities": ["Test"],
            "key_facts": [],  # Invalid: min_length=1
            "summary": "Too short",  # Invalid: min_length=10
            "confidence_score": 1.5  # Invalid: max value is 1.0
        }
        
        result = validate_structured_data(data, "data_extraction")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(error, ValidationError) for error in result)
    
    def test_schema_registry_completeness(self):
        """Test that all expected schemas are in the registry."""
        expected_schemas = {
            "data_extraction",
            "code_analysis",
            "configuration_task",
            "sentiment_analysis",
            "api_response",
            "error_response"
        }
        
        assert set(SCHEMA_REGISTRY.keys()) == expected_schemas
        
        # Test that all schemas can generate JSON schemas
        for schema_name in SCHEMA_REGISTRY:
            schema = get_json_schema(schema_name)
            assert isinstance(schema, dict)
            assert "properties" in schema


class TestSchemaEnums:
    """Test enum value validation."""
    
    def test_priority_level_values(self):
        """Test PriorityLevel enum values."""
        assert PriorityLevel.HIGH == "high"
        assert PriorityLevel.MEDIUM == "medium"
        assert PriorityLevel.LOW == "low"
        
        # Test validation in model
        data = {
            "task_name": "Test Task",
            "priority": "high",
            "steps": ["Step 1"],
            "estimated_duration": "1 hour",
            "validation_criteria": ["Criteria 1"]
        }
        
        model = ConfigurationTask.model_validate(data)
        assert model.priority == PriorityLevel.HIGH
    
    def test_sentiment_values(self):
        """Test Sentiment enum values."""
        assert Sentiment.POSITIVE == "positive"
        assert Sentiment.NEGATIVE == "negative"
        assert Sentiment.NEUTRAL == "neutral"
        assert Sentiment.MIXED == "mixed"
        
        # Test validation in model
        data = {
            "overall_sentiment": "positive",
            "confidence": 0.8,
            "key_phrases": ["good", "great"],
            "reasoning": "Positive language throughout the text indicates positive sentiment."
        }
        
        model = SentimentAnalysis.model_validate(data)
        assert model.overall_sentiment == Sentiment.POSITIVE
    
    def test_invalid_enum_values(self):
        """Test that invalid enum values are rejected."""
        # Invalid priority
        data = {
            "task_name": "Test Task",
            "priority": "invalid_priority",
            "steps": ["Step 1"],
            "estimated_duration": "1 hour",
            "validation_criteria": ["Criteria 1"]
        }
        
        with pytest.raises(Exception):
            ConfigurationTask.model_validate(data)
        
        # Invalid sentiment
        sentiment_data = {
            "overall_sentiment": "invalid_sentiment",
            "confidence": 0.8,
            "key_phrases": ["test"],
            "reasoning": "Test reasoning with sufficient length."
        }
        
        with pytest.raises(Exception):
            SentimentAnalysis.model_validate(sentiment_data)