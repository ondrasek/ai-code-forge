"""Perplexity API client implementation."""

import httpx
import os
import time
from typing import Dict, Any, List, Optional
from functools import wraps
import asyncio

from .utils.logging import get_logger, log_api_request, log_api_response, debug_decorator

logger = get_logger(__name__)


def handle_api_errors(func):
    """Enhanced decorator for handling Perplexity API errors with extensive logging."""
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
        except httpx.HTTPStatusError as e:
            duration = (time.time() - start_time) * 1000
            error_details = {
                "status_code": e.response.status_code,
                "response_text": e.response.text,
                "headers": dict(e.response.headers),
                "duration_ms": duration
            }
            
            if e.response.status_code == 429:
                logger.warning(f"Rate limit exceeded - {func_name} - {duration:.2f}ms")
                logger.debug(f"Rate limit details: {error_details}")
                return {"error": "Rate limit exceeded. Please try again later.", "details": error_details}
            elif e.response.status_code == 401:
                logger.error(f"Authentication failed - {func_name} - {duration:.2f}ms")
                logger.debug(f"Auth error details: {error_details}")
                return {"error": "Authentication failed. Check your API key.", "details": error_details}
            elif e.response.status_code == 400:
                logger.error(f"Bad request - {func_name} - {duration:.2f}ms: {e.response.text}")
                logger.debug(f"Bad request details: {error_details}")
                return {"error": f"Bad request: {e.response.text}", "details": error_details}
            else:
                logger.error(f"API error ({e.response.status_code}) - {func_name} - {duration:.2f}ms: {e.response.text}")
                logger.debug(f"General API error details: {error_details}")
                return {"error": f"API error ({e.response.status_code}): {e.response.text}", "details": error_details}
        except httpx.RequestError as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Network error - {func_name} - {duration:.2f}ms: {str(e)}")
            logger.debug(f"Network error details: {{'type': '{type(e).__name__}', 'message': '{str(e)}', 'duration_ms': {duration}}}")
            return {"error": f"Network error: {str(e)}", "details": {"type": type(e).__name__, "duration_ms": duration}}
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.exception(f"Unexpected error in API call - {func_name} - {duration:.2f}ms")
            logger.debug(f"Unexpected error details: {{'type': '{type(e).__name__}', 'message': '{str(e)}', 'duration_ms': {duration}}}")
            return {"error": f"Unexpected error: {str(e)}", "details": {"type": type(e).__name__, "duration_ms": duration}}
    return wrapper


class PerplexityClient:
    """Client for interacting with the Perplexity API."""
    
    AVAILABLE_MODELS = [
        "sonar",
        "sonar-pro", 
        "sonar-reasoning",
        "sonar-deep-research"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity client with enhanced debugging.
        
        Args:
            api_key: Perplexity API key. If not provided, will try to load from environment.
        """
        logger.debug("Initializing Perplexity client...")
        
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            logger.error("PERPLEXITY_API_KEY environment variable not found")
            raise ValueError("PERPLEXITY_API_KEY environment variable is required")
        
        # Log API key presence (but not the actual key)
        logger.debug(f"API key loaded: {'***' + self.api_key[-4:] if len(self.api_key) > 4 else '***'}")
            
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.timeout = float(os.getenv("PERPLEXITY_TIMEOUT", "60.0"))
        self.deep_research_timeout = float(os.getenv("PERPLEXITY_DEEP_RESEARCH_TIMEOUT", "300.0"))
        
        # Log configuration
        logger.debug(f"Client configuration: base_url={self.base_url}, timeout={self.timeout}s, deep_research_timeout={self.deep_research_timeout}s")
        logger.info("Perplexity client initialized successfully")
    
    @handle_api_errors
    async def query(
        self,
        prompt: str,
        model: str = "sonar",
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        top_k: int = 0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        return_citations: bool = True,
        return_images: bool = False,
        return_related_questions: bool = False,
        search_domain_filter: Optional[List[str]] = None,
        search_filter: Optional[str] = None,
        stream: bool = False,
        custom_timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Query the Perplexity API.
        
        Args:
            prompt: The user query
            model: Model to use (sonar, sonar-pro, sonar-reasoning, sonar-deep-research)
            system_message: Optional system message to customize behavior
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter (0.0 to 1.0)
            top_k: Number of top search results to consider (integer)
            presence_penalty: Penalty for token presence (-2.0 to 2.0)
            frequency_penalty: Penalty for token frequency (-2.0 to 2.0)
            return_citations: Whether to include citations
            return_images: Whether to include images in results
            return_related_questions: Whether to return related questions
            search_domain_filter: List of domains to search within
            search_filter: Search filter (e.g., "academic" for academic sources)
            stream: Whether to stream the response
            custom_timeout: Custom timeout for this request (overrides default)
            
        Returns:
            API response dictionary or error dictionary
        """
        if model not in self.AVAILABLE_MODELS:
            logger.warning(f"Unknown model '{model}', using 'sonar' instead")
            model = "sonar"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "return_citations": return_citations,
            "return_images": return_images,
            "return_related_questions": return_related_questions,
            "stream": stream
        }
        
        # Add optional search filters
        if search_domain_filter:
            data["search_domain_filter"] = search_domain_filter
        if search_filter:
            data["search_filter"] = search_filter
        
        # Determine timeout to use
        timeout_to_use = custom_timeout if custom_timeout is not None else (
            self.deep_research_timeout if model == "sonar-deep-research" else self.timeout
        )
        
        # Log API request details
        request_id = log_api_request("POST", self.base_url, headers, data)
        logger.debug(f"Making API request with model: {model}, timeout: {timeout_to_use}s, request_id: {request_id}")
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=timeout_to_use) as client:
                logger.debug(f"Sending HTTP POST to {self.base_url} with timeout {timeout_to_use}s")
                response = await client.post(self.base_url, headers=headers, json=data)
                duration = (time.time() - start_time) * 1000
                
                logger.debug(f"HTTP response received: status={response.status_code}, duration={duration:.2f}ms")
                
                response.raise_for_status()
                result = response.json()
                
                # Log successful response
                log_api_response(request_id, response.status_code, result, duration)
                
                tokens_used = result.get('usage', {}).get('total_tokens', 'unknown')
                logger.info(f"API request successful - tokens: {tokens_used}, duration: {duration:.2f}ms")
                logger.debug(f"Response structure: {list(result.keys()) if isinstance(result, dict) else type(result).__name__}")
                
                return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"API request failed after {duration:.2f}ms: {type(e).__name__}: {str(e)}")
            
            # Log failed response
            status_code = getattr(getattr(e, 'response', None), 'status_code', 0) if hasattr(e, 'response') else 0
            log_api_response(request_id, status_code, {}, duration, str(e))
            
            raise
    
    
    @debug_decorator
    async def health_check(self) -> bool:
        """
        Check if the API is accessible and credentials are valid with enhanced logging.
        
        Returns:
            True if API is accessible, False otherwise
        """
        logger.debug("Starting health check...")
        
        try:
            logger.debug("Sending test query to API")
            result = await self.query("Health check test query", max_tokens=10)
            
            is_healthy = "error" not in result
            logger.debug(f"Health check result: healthy={is_healthy}, response_keys={list(result.keys()) if isinstance(result, dict) else 'non-dict'}")
            
            if is_healthy:
                logger.info("Health check passed - API is accessible")
            else:
                logger.warning(f"Health check failed - API returned error: {result.get('error', 'unknown')}")
            
            return is_healthy
        except Exception as e:
            logger.error(f"Health check failed with exception: {type(e).__name__}: {str(e)}")
            logger.debug(f"Health check exception details", exc_info=True)
            return False