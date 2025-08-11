"""FastMCP server implementation for OpenAI structured output integration."""

import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError("FastMCP library is required. Install with: uv add fastmcp")

from .client import OpenAIStructuredClient
from .utils.logging import setup_logging, get_logger, debug_decorator
from .schemas import SCHEMA_REGISTRY

# Load environment variables
load_dotenv()

# Initialize logging with environment configuration
try:
    logger = setup_logging(
        log_level=os.getenv("OPENAI_STRUCTURED_LOG_LEVEL", "INFO"),
        logger_name="openai_structured_mcp"
    )
except (ValueError, OSError, PermissionError) as e:
    # Print to stderr and exit - logging configuration is invalid
    import sys
    print(f"FATAL: Logging configuration error: {e}", file=sys.stderr)
    print("Set OPENAI_STRUCTURED_LOG_LEVEL=none to disable logging", file=sys.stderr)
    sys.exit(1)

# Log environment configuration
logger.info("OpenAI Structured MCP server starting")
logger.debug(f"Environment variables:")
logger.debug(f"  OPENAI_STRUCTURED_LOG_LEVEL: {os.getenv('OPENAI_STRUCTURED_LOG_LEVEL', 'INFO')}")
logger.debug(f"  OPENAI_STRUCTURED_LOG_PATH: {os.getenv('OPENAI_STRUCTURED_LOG_PATH') or 'NOT_SET'}")
logger.debug(f"  OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT_SET'}")
logger.debug(f"  OPENAI_DEFAULT_MODEL: {os.getenv('OPENAI_DEFAULT_MODEL', 'gpt-5')}")
logger.debug(f"  OPENAI_DEFAULT_TEMPERATURE: {os.getenv('OPENAI_DEFAULT_TEMPERATURE', '0.7')}")

# Create FastMCP server instance
mcp = FastMCP("OpenAI Structured Output Server")

# Initialize OpenAI client
try:
    openai_client = OpenAIStructuredClient()
    logger.info("OpenAI Structured MCP server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    raise


@mcp.tool(
    annotations={
        "title": "Extract Structured Data",
        "description": "Extract structured data from unstructured text with guaranteed JSON format",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
@debug_decorator
async def extract_data(
    text: str,
    custom_instructions: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> str:
    """
    Extract structured data from unstructured text using OpenAI's structured output.
    
    Args:
        text: The text to analyze and extract data from
        custom_instructions: Optional custom instructions for the extraction process
        model: OpenAI model to use (defaults to configured model)
        temperature: Sampling temperature between 0.0-2.0 (defaults to configured temperature)
    
    Returns:
        JSON string with structured data extraction results including entities, facts, and summary
    """
    logger.info(f"Data extraction request: {len(text)} characters")
    logger.debug(f"Text preview: {text[:100]}...")
    
    try:
        result = await openai_client.extract_data(
            text=text,
            custom_instructions=custom_instructions
        )
        
        if "error" in result:
            logger.error(f"Data extraction failed: {result['error']}")
            return f"Error extracting data: {result['error']}"
        
        logger.info(f"Data extraction completed successfully")
        logger.debug(f"Extracted entities count: {len(result['data'].get('entities', []))}")
        
        # Return formatted JSON string
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error during data extraction: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Data extraction exception details", exc_info=True)
        return error_msg


@mcp.tool(
    annotations={
        "title": "Analyze Code Structure",
        "description": "Analyze code for complexity, issues, and recommendations with structured output",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
@debug_decorator
async def analyze_code(
    code: str,
    language_hint: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> str:
    """
    Analyze source code and provide structured feedback on complexity, issues, and improvements.
    
    Args:
        code: The source code to analyze
        language_hint: Optional hint about the programming language (e.g., 'python', 'javascript')
        model: OpenAI model to use (defaults to configured model)
        temperature: Sampling temperature between 0.0-2.0 (defaults to configured temperature)
    
    Returns:
        JSON string with structured code analysis including complexity score, issues, and recommendations
    """
    logger.info(f"Code analysis request: {len(code)} characters, language_hint: {language_hint}")
    logger.debug(f"Code preview: {code[:200]}...")
    
    try:
        result = await openai_client.analyze_code(
            code=code,
            language_hint=language_hint
        )
        
        if "error" in result:
            logger.error(f"Code analysis failed: {result['error']}")
            return f"Error analyzing code: {result['error']}"
        
        logger.info(f"Code analysis completed successfully")
        logger.debug(f"Complexity score: {result['data'].get('complexity_score')}, Issues: {len(result['data'].get('issues', []))}")
        
        # Return formatted JSON string
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error during code analysis: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Code analysis exception details", exc_info=True)
        return error_msg


@mcp.tool(
    annotations={
        "title": "Create Configuration Task",
        "description": "Create structured configuration tasks with steps and validation criteria",
        "readOnlyHint": False,
        "openWorldHint": False
    }
)
@debug_decorator
async def create_configuration_task(
    description: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> str:
    """
    Create a structured configuration task from a high-level description.
    
    Args:
        description: Description of the configuration task or requirements
        model: OpenAI model to use (defaults to configured model)
        temperature: Sampling temperature between 0.0-2.0 (defaults to configured temperature)
    
    Returns:
        JSON string with structured task definition including steps, priorities, and validation criteria
    """
    logger.info(f"Configuration task creation request: {len(description)} characters")
    logger.debug(f"Task description: {description}")
    
    try:
        result = await openai_client.create_configuration_task(
            description=description
        )
        
        if "error" in result:
            logger.error(f"Configuration task creation failed: {result['error']}")
            return f"Error creating configuration task: {result['error']}"
        
        logger.info(f"Configuration task created successfully")
        logger.debug(f"Task name: {result['data'].get('task_name')}, Steps: {len(result['data'].get('steps', []))}")
        
        # Return formatted JSON string
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error creating configuration task: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Configuration task exception details", exc_info=True)
        return error_msg


@mcp.tool(
    annotations={
        "title": "Analyze Sentiment",
        "description": "Analyze text sentiment with detailed emotional breakdown and reasoning",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
@debug_decorator
async def analyze_sentiment(
    text: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> str:
    """
    Analyze the sentiment of text with detailed emotional breakdown and confidence scoring.
    
    Args:
        text: The text to analyze for sentiment
        model: OpenAI model to use (defaults to configured model)
        temperature: Sampling temperature between 0.0-2.0 (defaults to configured temperature)
    
    Returns:
        JSON string with structured sentiment analysis including overall sentiment, emotions, and reasoning
    """
    logger.info(f"Sentiment analysis request: {len(text)} characters")
    logger.debug(f"Text preview: {text[:100]}...")
    
    try:
        result = await openai_client.analyze_sentiment(
            text=text
        )
        
        if "error" in result:
            logger.error(f"Sentiment analysis failed: {result['error']}")
            return f"Error analyzing sentiment: {result['error']}"
        
        logger.info(f"Sentiment analysis completed successfully")
        logger.debug(f"Overall sentiment: {result['data'].get('overall_sentiment')}, Confidence: {result['data'].get('confidence')}")
        
        # Return formatted JSON string
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error during sentiment analysis: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Sentiment analysis exception details", exc_info=True)
        return error_msg


@mcp.tool(
    annotations={
        "title": "Custom Structured Query",
        "description": "Execute custom query with any available schema for maximum flexibility",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
@debug_decorator
async def custom_structured_query(
    prompt: str,
    schema_name: str,
    system_message: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> str:
    """
    Execute a custom query using any available schema for structured output.
    
    Args:
        prompt: The query or prompt to process
        schema_name: Name of the schema to use (data_extraction, code_analysis, configuration_task, sentiment_analysis)
        system_message: Optional custom system message to guide the response
        model: OpenAI model to use (defaults to configured model)
        temperature: Sampling temperature between 0.0-2.0 (defaults to configured temperature)
        max_tokens: Maximum tokens in response (defaults to configured max_tokens)
    
    Returns:
        JSON string with structured response according to the specified schema
    """
    logger.info(f"Custom structured query: schema={schema_name}, prompt_length={len(prompt)}")
    logger.debug(f"Available schemas: {list(SCHEMA_REGISTRY.keys())}")
    
    try:
        result = await openai_client.structured_completion(
            prompt=prompt,
            schema_name=schema_name,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if "error" in result:
            logger.error(f"Custom structured query failed: {result['error']}")
            return f"Error in custom query: {result['error']}"
        
        logger.info(f"Custom structured query completed successfully")
        
        # Return formatted JSON string
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error during custom structured query: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Custom query exception details", exc_info=True)
        return error_msg


@mcp.tool(
    annotations={
        "title": "List Available Schemas",
        "description": "Get information about all available schemas for structured output",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
@debug_decorator
async def list_schemas() -> str:
    """
    List all available schemas and their descriptions.
    
    Returns:
        Formatted information about available schemas and their use cases
    """
    schemas_info = openai_client.get_available_schemas()
    
    result = "**Available Structured Output Schemas:**\n\n"
    for schema_name, description in schemas_info.items():
        result += f"• **{schema_name}**: {description}\n\n"
    
    result += "\n**Usage Tips:**\n"
    result += "• Use 'data_extraction' for extracting structured information from unstructured text\n"
    result += "• Use 'code_analysis' for analyzing source code quality and complexity\n"
    result += "• Use 'configuration_task' for breaking down tasks into structured steps\n"
    result += "• Use 'sentiment_analysis' for detailed emotion and sentiment analysis\n"
    result += "• Use 'custom_structured_query' with any schema for maximum flexibility\n"
    
    logger.debug(f"Schema list generated, length: {len(result)}")
    return result


@mcp.tool(
    annotations={
        "title": "Health Check",
        "description": "Check if OpenAI API is accessible and working with structured outputs",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
@debug_decorator
async def health_check() -> str:
    """
    Check the health status of the OpenAI API connection and structured output capability.
    
    Returns:
        Status message indicating if the API is accessible and structured outputs are working
    """
    logger.info("Performing health check")
    logger.debug("Starting comprehensive health check of OpenAI API connection")
    
    # Check logging status
    log_level = os.getenv("OPENAI_STRUCTURED_LOG_LEVEL", "INFO").upper()
    log_path = os.getenv("OPENAI_STRUCTURED_LOG_PATH")
    
    if log_level == "NONE" or not log_level:
        log_status = "disabled (OPENAI_STRUCTURED_LOG_LEVEL=none)"
    elif not log_path:
        log_status = "disabled (OPENAI_STRUCTURED_LOG_PATH not set)"
    elif logger.disabled:
        log_status = "disabled (configuration error)"
    else:
        log_status = f"enabled (level={log_level}, path={log_path})"
    
    try:
        # Test basic API connectivity
        is_healthy = await openai_client.health_check()
        
        if is_healthy:
            # Test structured output capability
            logger.debug("Testing structured output capability...")
            test_result = await openai_client.structured_completion(
                prompt="Test structured output with a simple example.",
                schema_name="data_extraction",
                system_message="Extract any entities, provide one key fact, and summarize in one sentence.",
                max_tokens=200,
                temperature=0.0
            )
            
            if "error" in test_result:
                logger.debug("Structured output test failed")
                return f"❌ Basic API works but structured output failed: {test_result['error']}\n📁 Logging: {log_status}"
            else:
                logger.debug("Health check passed - API and structured outputs working")
                return f"✅ OpenAI API is accessible and structured outputs are working correctly.\n📁 Logging: {log_status}"
        else:
            logger.debug("Health check failed - API is not responding correctly")
            return f"❌ OpenAI API is not responding correctly. Check your API key and network connection.\n📁 Logging: {log_status}"
            
    except Exception as e:
        error_msg = f"❌ Health check failed: {str(e)}\n📁 Logging: {log_status}"
        logger.error(error_msg)
        logger.debug(f"Health check exception details", exc_info=True)
        return error_msg


# Entry point for stdio transport
def main():
    """Main entry point for the MCP server with enhanced logging."""
    logger.info("Starting OpenAI Structured MCP server...")
    logger.debug(f"Server configuration: FastMCP instance={type(mcp).__name__}")
    logger.debug(f"Available tools: {[tool for tool in dir(mcp) if not tool.startswith('_')]}")
    
    try:
        logger.debug("Starting FastMCP server with stdio transport")
        mcp.run()  # Defaults to stdio transport
    except KeyboardInterrupt:
        logger.info("Server stopped by user (KeyboardInterrupt)")
        logger.debug("Graceful shutdown initiated")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.debug(f"Server exception details", exc_info=True)
        raise
    finally:
        logger.debug("Server shutdown complete")


if __name__ == "__main__":
    main()