"""OpenAI API client implementation with structured output support."""

import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from functools import wraps

try:
    from openai import AsyncOpenAI
except ImportError:
    raise ImportError("OpenAI library is required. Install with: uv add openai")

from .utils.logging import get_logger, log_api_request, log_api_response, debug_decorator
from .schemas import get_json_schema, validate_structured_data, SCHEMA_REGISTRY

logger = get_logger(__name__)


def handle_api_errors(func):
    """Enhanced decorator for handling OpenAI API errors with extensive logging."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        logger.debug(f"Starting API call: {func_name}")
        
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"API call completed successfully: {func_name} - {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            # Handle different types of OpenAI API errors
            if hasattr(e, 'response'):
                status_code = getattr(e.response, 'status_code', 0)
                response_text = getattr(e.response, 'text', str(e))
                
                if status_code == 429:
                    logger.warning(f"Rate limit exceeded - {func_name} - {duration:.2f}ms")
                    return {"error": "Rate limit exceeded. Please try again later.", "error_type": "rate_limit"}
                elif status_code == 401:
                    logger.error(f"Authentication failed - {func_name} - {duration:.2f}ms")
                    return {"error": "Authentication failed. Check your API key.", "error_type": "authentication"}
                elif status_code == 400:
                    logger.error(f"Bad request - {func_name} - {duration:.2f}ms: {response_text}")
                    return {"error": f"Bad request: {response_text}", "error_type": "bad_request"}
                else:
                    logger.error(f"API error ({status_code}) - {func_name} - {duration:.2f}ms: {response_text}")
                    return {"error": f"API error ({status_code}): {response_text}", "error_type": "api_error"}
            else:
                logger.error(f"Unexpected error - {func_name} - {duration:.2f}ms: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}", "error_type": "unexpected"}
    return wrapper


class OpenAIStructuredClient:
    """Client for interacting with OpenAI API using structured outputs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client with enhanced debugging.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to load from environment.
        """
        logger.debug("Initializing OpenAI structured client...")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY environment variable not found")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Log API key presence (no actual key data)
        logger.debug("API key loaded successfully")
        
        # Initialize async client
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Configuration
        self.default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5")
        self.default_temperature = float(os.getenv("OPENAI_DEFAULT_TEMPERATURE", "0.7"))
        self.default_max_tokens = int(os.getenv("OPENAI_DEFAULT_MAX_TOKENS", "1000"))
        
        logger.debug(f"Client configuration: model={self.default_model}, temperature={self.default_temperature}, max_tokens={self.default_max_tokens}")
        logger.info("OpenAI structured client initialized successfully")
    
    async def get_available_models(self) -> List[str]:
        """
        Fetch available models from OpenAI API dynamically.
        
        Returns:
            List of available model names
        """
        try:
            logger.debug("Fetching available models from OpenAI API...")
            models_response = await self.client.models.list()
            models = [model.id for model in models_response.data]
            logger.debug(f"Fetched {len(models)} models from OpenAI API")
            return models
        except Exception as e:
            logger.error(f"Failed to fetch models from OpenAI API: {e}")
            # Fallback to a minimal set if API fails
            fallback_models = ["gpt-5", "gpt-4o", "gpt-4o-mini"]
            logger.warning(f"Using fallback models: {fallback_models}")
            return fallback_models
    
    @handle_api_errors
    async def structured_completion(
        self,
        prompt: str,
        schema_name: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        validate_response: bool = True
    ) -> Dict[str, Any]:
        """
        Generate structured completion using OpenAI's JSON Schema validation.
        
        Args:
            prompt: User prompt/query
            schema_name: Name of the schema to use from SCHEMA_REGISTRY
            system_message: Optional system message
            model: OpenAI model to use (defaults to configured default)
            temperature: Sampling temperature (defaults to configured default)
            max_tokens: Maximum tokens in response (defaults to configured default)
            validate_response: Whether to validate response against schema
            
        Returns:
            API response dictionary with structured data
        """
        # Get schema
        try:
            json_schema = get_json_schema(schema_name)
        except KeyError as e:
            logger.error(f"Invalid schema name: {schema_name}")
            return {
                "error": str(e),
                "error_type": "invalid_schema",
                "available_schemas": list(SCHEMA_REGISTRY.keys())
            }
        
        # Use provided parameters or defaults
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        # Validate model against OpenAI API
        available_models = await self.get_available_models()
        if model not in available_models:
            logger.warning(f"Unknown model '{model}', using '{self.default_model}' instead")
            model = self.default_model
        
        # Build messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request data
        request_data = {
            "model": model,
            "messages": messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": json_schema
                }
            },
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Log request
        request_id = log_api_request(
            "POST", 
            "https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            request_data
        )
        
        logger.debug(f"Making structured completion request: schema={schema_name}, model={model}, request_id={request_id}")
        
        start_time = time.time()
        try:
            # Make API call
            response = await self.client.chat.completions.create(**request_data)
            duration = (time.time() - start_time) * 1000
            
            logger.debug(f"OpenAI response received: duration={duration:.2f}ms")
            
            # Convert response to dict
            response_dict = response.model_dump()
            
            # Log successful response
            log_api_response(request_id, 200, response_dict, duration)
            
            # Extract structured content
            if response_dict.get("choices") and len(response_dict["choices"]) > 0:
                content = response_dict["choices"][0].get("message", {}).get("content")
                
                if content:
                    try:
                        # Parse JSON content
                        import json
                        structured_data = json.loads(content)
                        
                        # Validate if requested
                        if validate_response:
                            validation_result = validate_structured_data(structured_data, schema_name)
                            if isinstance(validation_result, list):  # Validation errors
                                logger.warning(f"Response validation failed for schema {schema_name}")
                                return {
                                    "error": "Response validation failed",
                                    "error_type": "validation_error",
                                    "validation_errors": [error.model_dump() for error in validation_result],
                                    "raw_response": structured_data
                                }
                        
                        # Success response
                        result = {
                            "success": True,
                            "data": structured_data,
                            "metadata": {
                                "schema_name": schema_name,
                                "model": model,
                                "temperature": temperature,
                                "max_tokens": max_tokens,
                                "finish_reason": response_dict["choices"][0].get("finish_reason")
                            },
                            "timestamp": datetime.now().isoformat(),
                            "processing_time_ms": duration,
                            "usage": response_dict.get("usage", {})
                        }
                        
                        logger.info(f"Structured completion successful: {schema_name}, tokens={result['usage'].get('total_tokens', 0)}, duration={duration:.2f}ms")
                        return result
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        return {
                            "error": f"Invalid JSON response: {e}",
                            "error_type": "json_parse_error",
                            "raw_content": content
                        }
                else:
                    logger.error("Empty content in API response")
                    return {"error": "Empty response content", "error_type": "empty_response"}
            else:
                logger.error("No choices in API response")
                return {"error": "No response choices", "error_type": "no_choices"}
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Structured completion failed after {duration:.2f}ms: {type(e).__name__}: {str(e)}")
            
            # Log failed response
            log_api_response(request_id, 0, {}, duration, str(e))
            
            raise
    
    @debug_decorator
    async def extract_data(self, text: str, custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured data from unstructured text.
        
        Args:
            text: Text to analyze and extract data from
            custom_instructions: Optional custom instructions for extraction
            
        Returns:
            Structured data extraction results
        """
        system_message = f"""Extract structured data from the provided text.
        Focus on identifying named entities, key facts, and providing a concise summary.
        Assign a confidence score based on how clearly extractable the information is.
        
        {custom_instructions or 'Use your best judgment for extraction.'}"""
        
        return await self.structured_completion(
            prompt=text,
            schema_name="data_extraction",
            system_message=system_message
        )
    
    @debug_decorator
    async def analyze_code(self, code: str, language_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze code structure and quality.
        
        Args:
            code: Source code to analyze
            language_hint: Optional hint about the programming language
            
        Returns:
            Structured code analysis results
        """
        lang_instruction = f" The code is in {language_hint}." if language_hint else ""
        
        system_message = f"""Analyze the provided source code for complexity, issues, strengths, and recommendations.
        Provide a complexity score from 1-10 and count functions/methods and lines of code.{lang_instruction}
        Be specific in your recommendations and focus on actionable improvements."""
        
        return await self.structured_completion(
            prompt=code,
            schema_name="code_analysis",
            system_message=system_message
        )
    
    @debug_decorator
    async def create_configuration_task(self, description: str) -> Dict[str, Any]:
        """
        Create a structured configuration task from a description.
        
        Args:
            description: Task description or requirements
            
        Returns:
            Structured configuration task definition
        """
        system_message = """Convert the task description into a structured configuration task.
        Break it down into specific, actionable steps with clear prerequisites and validation criteria.
        Assign an appropriate priority level and provide a realistic time estimate."""
        
        return await self.structured_completion(
            prompt=description,
            schema_name="configuration_task",
            system_message=system_message
        )
    
    @debug_decorator
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text with detailed emotional breakdown.
        
        Args:
            text: Text to analyze for sentiment
            
        Returns:
            Structured sentiment analysis results
        """
        system_message = """Analyze the sentiment of the provided text.
        Provide an overall sentiment classification with confidence score.
        Identify key phrases that influenced the analysis and break down specific emotions.
        Include clear reasoning for your sentiment classification."""
        
        return await self.structured_completion(
            prompt=text,
            schema_name="sentiment_analysis",
            system_message=system_message
        )
    
    @debug_decorator
    async def health_check(self) -> bool:
        """
        Check if the OpenAI API is accessible and credentials are valid.
        
        Returns:
            True if API is accessible, False otherwise
        """
        logger.debug("Starting health check...")
        
        try:
            # Simple completion to test API access
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "Say 'healthy' if you receive this."}],
                max_tokens=10,
                temperature=0.0
            )
            
            # Check if we got a reasonable response
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                is_healthy = content and "healthy" in content.lower()
                
                if is_healthy:
                    logger.info("Health check passed - API is accessible")
                else:
                    logger.warning(f"Health check questionable - unexpected response: {content}")
                    
                return is_healthy
            else:
                logger.error("Health check failed - no response choices")
                return False
                
        except Exception as e:
            logger.error(f"Health check failed with exception: {type(e).__name__}: {str(e)}")
            return False
    
    def get_available_schemas(self) -> Dict[str, str]:
        """
        Get information about available schemas.
        
        Returns:
            Dictionary mapping schema names to their descriptions
        """
        return {
            "data_extraction": "Extract structured data from unstructured text",
            "code_analysis": "Analyze code structure, complexity, and quality",
            "configuration_task": "Create structured configuration tasks with steps and validation",
            "sentiment_analysis": "Analyze sentiment with emotional breakdown and reasoning"
        }