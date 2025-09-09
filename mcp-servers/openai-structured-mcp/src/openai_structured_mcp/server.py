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

# Initialize OpenAI client lazily
openai_client = None

def get_openai_client():
    """Get or create the OpenAI client instance."""
    global openai_client
    if openai_client is None:
        try:
            openai_client = OpenAIStructuredClient()
            logger.info("OpenAI Structured MCP server initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    return openai_client


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
        result = await get_openai_client().extract_data(
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
        result = await get_openai_client().analyze_code(
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
        result = await get_openai_client().create_configuration_task(
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
        result = await get_openai_client().analyze_sentiment(
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
        result = await get_openai_client().structured_completion(
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
    schemas_info = await get_openai_client().get_available_schemas()
    
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


# === CODEX INTEGRATION TOOLS ===


@mcp.tool(
    annotations={
        "title": "Codex Generate Code",
        "description": "Generate code using Codex-optimized prompting strategies",
        "readOnlyHint": False,
        "openWorldHint": False
    }
)
@debug_decorator
async def codex_generate(
    prompt: str,
    language: Optional[str] = None,
    context: Optional[str] = None,
    style: Optional[str] = "clean",
    model: Optional[str] = None,
    temperature: Optional[float] = 0.2
) -> str:
    """
    Generate code using Codex-optimized prompting for high-quality, production-ready code.
    
    Args:
        prompt: Description of the code to generate
        language: Target programming language (e.g., 'python', 'javascript', 'rust')
        context: Optional context or existing code to build upon
        style: Code style preference ('clean', 'documented', 'minimal', 'enterprise')
        model: OpenAI model to use (defaults to configured model)
        temperature: Sampling temperature, lower for more deterministic code (default: 0.2)
    
    Returns:
        Generated code with explanation and usage notes
    """
    logger.info(f"Codex code generation request: language={language}, style={style}")
    logger.debug(f"Prompt preview: {prompt[:100]}...")
    
    # Build Codex-optimized system message
    codex_system = f"""You are OpenAI Codex, an expert code generation AI. Generate {language or 'appropriate'} code that is:
- Production-ready and well-structured
- Follows best practices and idioms for {language or 'the target language'}
- Includes proper error handling where applicable
- Uses clear, descriptive variable and function names
- Style preference: {style}

Respond with the code and a brief explanation of key design decisions."""

    # Enhanced prompt with context
    enhanced_prompt = f"""Generate {language or ''} code for: {prompt}

{f"Existing context to build upon: {context}" if context else ""}

Requirements:
- Write clean, readable, maintainable code
- Include necessary imports/dependencies
- Add brief inline comments for complex logic
- Consider error handling and edge cases"""

    try:
        # Use OpenAI API directly for Codex-style generation
        import json
        from openai import AsyncOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set"
        
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model=model or os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
            messages=[
                {"role": "system", "content": codex_system},
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=temperature,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        logger.info("Codex code generation completed successfully")
        
        return result
        
    except Exception as e:
        error_msg = f"Error during Codex code generation: {str(e)}"
        logger.error(error_msg)
        logger.debug("Codex generation exception details", exc_info=True)
        return error_msg


@mcp.tool(
    annotations={
        "title": "Codex Review Code", 
        "description": "Perform comprehensive code review with Codex-level analysis",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
@debug_decorator
async def codex_review(
    code: str,
    language_hint: Optional[str] = None,
    focus: Optional[str] = "comprehensive",
    model: Optional[str] = None,
    temperature: Optional[float] = 0.3
) -> str:
    """
    Perform Codex-level code review with detailed analysis and actionable feedback.
    
    Args:
        code: Source code to review
        language_hint: Programming language hint for better analysis
        focus: Review focus ('security', 'performance', 'maintainability', 'comprehensive')
        model: OpenAI model to use (defaults to configured model)
        temperature: Sampling temperature for analysis variability (default: 0.3)
    
    Returns:
        Structured code review with ratings, issues, and improvement suggestions
    """
    logger.info(f"Codex code review request: language={language_hint}, focus={focus}")
    logger.debug(f"Code length: {len(code)} characters")
    
    # Build Codex-optimized review prompt
    codex_system = f"""You are OpenAI Codex performing a professional code review. Analyze the code with focus on: {focus}

Provide a structured review covering:
1. Overall Assessment (1-10 rating)
2. Strengths (what's done well)
3. Issues Found (with severity: Critical/High/Medium/Low)
4. Security Concerns (if any)
5. Performance Considerations
6. Maintainability & Readability
7. Specific Improvement Recommendations
8. Code Quality Score (1-10)

Be thorough but constructive in your feedback."""

    enhanced_prompt = f"""Review this {language_hint or 'code'}:

```{language_hint or 'text'}
{code}
```

Focus areas for this review: {focus}
Provide actionable feedback that would help improve code quality in production."""

    try:
        # Use OpenAI API for comprehensive analysis
        import json
        from openai import AsyncOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set"
        
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model=model or os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
            messages=[
                {"role": "system", "content": codex_system},
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=temperature,
            max_tokens=1500
        )
        
        result = response.choices[0].message.content
        logger.info("Codex code review completed successfully")
        
        return result
        
    except Exception as e:
        error_msg = f"Error during Codex code review: {str(e)}"
        logger.error(error_msg)
        logger.debug("Codex review exception details", exc_info=True)
        return error_msg


@mcp.tool(
    annotations={
        "title": "Codex Refactor Code",
        "description": "Refactor existing code with Codex-level optimization and modernization",
        "readOnlyHint": False,
        "openWorldHint": False
    }
)
@debug_decorator
async def codex_refactor(
    code: str,
    requirements: str,
    language_hint: Optional[str] = None,
    preserve_behavior: bool = True,
    model: Optional[str] = None,
    temperature: Optional[float] = 0.1
) -> str:
    """
    Refactor code using Codex-level analysis with specific improvement requirements.
    
    Args:
        code: Source code to refactor
        requirements: Specific refactoring requirements or goals
        language_hint: Programming language hint for better refactoring
        preserve_behavior: Whether to maintain exact behavioral compatibility (default: True)
        model: OpenAI model to use (defaults to configured model)
        temperature: Low temperature for consistent refactoring (default: 0.1)
    
    Returns:
        Refactored code with explanation of changes and improvements made
    """
    logger.info(f"Codex refactoring request: language={language_hint}, preserve_behavior={preserve_behavior}")
    logger.debug(f"Requirements: {requirements[:100]}...")
    
    # Build Codex-optimized refactoring prompt
    codex_system = f"""You are OpenAI Codex performing professional code refactoring. Your goal: {requirements}

Refactoring principles:
- {'Preserve exact behavior and functionality' if preserve_behavior else 'Improve behavior while meeting new requirements'}
- Improve code quality, readability, and maintainability
- Follow modern {language_hint or 'language'} best practices
- Optimize performance where possible
- Reduce complexity and technical debt

Provide:
1. The refactored code
2. Summary of changes made
3. Explanation of improvements
4. Any breaking changes (if preserve_behavior=False)"""

    enhanced_prompt = f"""Refactor this {language_hint or 'code'} according to these requirements:

**Requirements:** {requirements}

**Original Code:**
```{language_hint or 'text'}
{code}
```

**Behavioral Preservation:** {'Must maintain exact same behavior' if preserve_behavior else 'Can modify behavior to meet requirements'}

Provide the refactored code with clear explanations of improvements."""

    try:
        # Use OpenAI API for intelligent refactoring
        from openai import AsyncOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set"
        
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model=model or os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
            messages=[
                {"role": "system", "content": codex_system},
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=temperature,
            max_tokens=2500
        )
        
        result = response.choices[0].message.content
        logger.info("Codex refactoring completed successfully")
        
        return result
        
    except Exception as e:
        error_msg = f"Error during Codex refactoring: {str(e)}"
        logger.error(error_msg)
        logger.debug("Codex refactoring exception details", exc_info=True)
        return error_msg


@mcp.tool(
    annotations={
        "title": "Codex Explain Code",
        "description": "Explain code functionality with Codex-level detail and insights",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
@debug_decorator
async def codex_explain(
    code: str,
    language_hint: Optional[str] = None,
    level: str = "detailed",
    audience: str = "developer",
    model: Optional[str] = None,
    temperature: Optional[float] = 0.4
) -> str:
    """
    Explain code functionality with comprehensive analysis and educational insights.
    
    Args:
        code: Source code to explain
        language_hint: Programming language hint for context
        level: Explanation level ('brief', 'detailed', 'expert', 'beginner')
        audience: Target audience ('developer', 'student', 'manager', 'technical-lead')
        model: OpenAI model to use (defaults to configured model) 
        temperature: Temperature for explanation variety (default: 0.4)
    
    Returns:
        Comprehensive code explanation tailored to the specified level and audience
    """
    logger.info(f"Codex explanation request: level={level}, audience={audience}, language={language_hint}")
    logger.debug(f"Code length: {len(code)} characters")
    
    # Build audience and level-appropriate system message
    audience_context = {
        "developer": "Assume solid programming knowledge. Focus on implementation details, patterns, and trade-offs.",
        "student": "Assume learning programming. Explain concepts clearly with educational context.",
        "manager": "Focus on high-level functionality, business value, and technical risks/benefits.",
        "technical-lead": "Emphasize architecture, scalability, maintenance implications, and technical decisions."
    }
    
    level_context = {
        "brief": "Provide a concise overview of main functionality and purpose.",
        "detailed": "Provide thorough explanation of logic, data flow, and key implementation details.",
        "expert": "Deep technical analysis including patterns, optimizations, and advanced concepts.",
        "beginner": "Step-by-step explanation with foundational concepts and learning guidance."
    }
    
    codex_system = f"""You are OpenAI Codex providing code explanation for {audience} at {level} level.

Audience context: {audience_context.get(audience, audience_context['developer'])}
Detail level: {level_context.get(level, level_context['detailed'])}

Provide explanation covering:
- High-level purpose and functionality
- Key algorithms or logic patterns
- Data flow and transformations
- Important implementation details
- Potential issues or considerations
- Learning insights (for educational contexts)

Tailor language and depth to the specified audience and level."""

    enhanced_prompt = f"""Explain this {language_hint or 'code'} for {audience} at {level} level:

```{language_hint or 'text'}
{code}
```

Focus on helping {audience} understand the code's purpose, implementation, and significance."""

    try:
        # Use OpenAI API for comprehensive explanation
        from openai import AsyncOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set"
        
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model=model or os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
            messages=[
                {"role": "system", "content": codex_system},
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=temperature,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        logger.info("Codex explanation completed successfully")
        
        return result
        
    except Exception as e:
        error_msg = f"Error during Codex explanation: {str(e)}"
        logger.error(error_msg)
        logger.debug("Codex explanation exception details", exc_info=True)
        return error_msg


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
        is_healthy = await get_openai_client().health_check()
        
        if is_healthy:
            # Test structured output capability
            logger.debug("Testing structured output capability...")
            test_result = await get_openai_client().structured_completion(
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