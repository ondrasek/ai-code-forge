# OpenAI Structured Output MCP Server

An experimental Model Context Protocol (MCP) server that demonstrates structured output capabilities using OpenAI's JSON Schema validation features. This server showcases how structured outputs can improve reliability and predictability in AI-assisted workflows.

## Features

### Structured Output Types

- **Data Extraction**: Extract entities, key facts, and summaries from unstructured text with confidence scoring
- **Code Analysis**: Analyze code complexity, identify issues, strengths, and recommendations with metrics
- **Configuration Tasks**: Break down tasks into structured steps with prerequisites and validation criteria
- **Sentiment Analysis**: Detailed sentiment analysis with emotional breakdown and confidence scoring

### Key Benefits

- **Guaranteed JSON Format**: All responses follow strict JSON Schema validation
- **Type Safety**: Pydantic models ensure data consistency and validation
- **Error Handling**: Comprehensive error handling with structured error responses
- **Flexibility**: Custom structured queries with any available schema
- **Observability**: Detailed logging with API request/response tracking

## Installation

### Prerequisites

- Python 3.13+
- OpenAI API key
- UV package manager (recommended)

### Setup

1. **Clone and navigate to the server directory:**
   ```bash
   cd src/openai-structured-mcp
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export OPENAI_STRUCTURED_LOG_LEVEL="INFO"
   export OPENAI_STRUCTURED_LOG_PATH="./logs"
   ```

### Environment Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | None | Yes |
| `OPENAI_DEFAULT_MODEL` | Default OpenAI model | `gpt-5` | No |
| `OPENAI_DEFAULT_TEMPERATURE` | Default sampling temperature | `0.7` | No |
| `OPENAI_DEFAULT_MAX_TOKENS` | Default max tokens | `1000` | No |
| `OPENAI_STRUCTURED_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL, none) | `INFO` | No |
| `OPENAI_STRUCTURED_LOG_PATH` | Log file directory path | None | Required if logging enabled |

## Usage

### Running the Server

```bash
uv run openai-structured-mcp
```

The server runs using stdio transport, compatible with MCP-enabled applications like Claude Desktop.

### Available Tools

#### 1. Extract Structured Data

**Tool**: `extract_data`

**Purpose**: Extract structured information from unstructured text

**Parameters**:
- `text` (required): Text to analyze and extract data from
- `custom_instructions` (optional): Custom instructions for extraction
- `model` (optional): OpenAI model to use
- `temperature` (optional): Sampling temperature

**Output**: JSON with entities, key facts, summary, and confidence score

**Example**:
```json
{
  "success": true,
  "data": {
    "entities": ["OpenAI", "GPT-4", "API"],
    "key_facts": [
      "OpenAI released GPT-4 with improved capabilities",
      "New model supports structured outputs"
    ],
    "summary": "OpenAI's GPT-4 offers enhanced structured output capabilities.",
    "confidence_score": 0.92
  },
  "metadata": {"schema_name": "data_extraction"},
  "timestamp": "2024-01-01T12:00:00",
  "processing_time_ms": 150.0
}
```

#### 2. Analyze Code Structure

**Tool**: `analyze_code`

**Purpose**: Analyze source code for complexity, issues, and improvements

**Parameters**:
- `code` (required): Source code to analyze
- `language_hint` (optional): Programming language hint
- `model` (optional): OpenAI model to use
- `temperature` (optional): Sampling temperature

**Output**: JSON with language detection, complexity score, issues, strengths, and recommendations

**Example**:
```json
{
  "success": true,
  "data": {
    "language": "python",
    "complexity_score": 4,
    "issues": ["Missing docstrings", "No type hints"],
    "strengths": ["Clear variable names", "Good error handling"],
    "recommendations": ["Add type annotations", "Include comprehensive docstrings"],
    "functions_count": 3,
    "lines_of_code": 25
  },
  "metadata": {"schema_name": "code_analysis"},
  "timestamp": "2024-01-01T12:00:00",
  "processing_time_ms": 200.0
}
```

#### 3. Create Configuration Task

**Tool**: `create_configuration_task`

**Purpose**: Convert task descriptions into structured configuration tasks

**Parameters**:
- `description` (required): Task description or requirements
- `model` (optional): OpenAI model to use
- `temperature` (optional): Sampling temperature

**Output**: JSON with structured task definition including steps, priority, and validation criteria

**Example**:
```json
{
  "success": true,
  "data": {
    "task_name": "Setup CI/CD Pipeline",
    "priority": "high",
    "steps": [
      "Create GitHub Actions workflow",
      "Configure build stages",
      "Setup deployment targets",
      "Test pipeline execution"
    ],
    "prerequisites": ["GitHub repository access", "Docker knowledge"],
    "estimated_duration": "4 hours",
    "validation_criteria": [
      "Pipeline runs without errors",
      "Automated tests pass"
    ]
  },
  "metadata": {"schema_name": "configuration_task"},
  "timestamp": "2024-01-01T12:00:00",
  "processing_time_ms": 180.0
}
```

#### 4. Analyze Sentiment

**Tool**: `analyze_sentiment`

**Purpose**: Analyze text sentiment with detailed emotional breakdown

**Parameters**:
- `text` (required): Text to analyze for sentiment
- `model` (optional): OpenAI model to use
- `temperature` (optional): Sampling temperature

**Output**: JSON with sentiment classification, confidence, key phrases, emotions, and reasoning

**Example**:
```json
{
  "success": true,
  "data": {
    "overall_sentiment": "positive",
    "confidence": 0.89,
    "key_phrases": ["excellent service", "highly recommend"],
    "emotions": {
      "joy": 0.8,
      "satisfaction": 0.9,
      "enthusiasm": 0.7
    },
    "reasoning": "Multiple positive indicators and enthusiastic language suggest strong positive sentiment."
  },
  "metadata": {"schema_name": "sentiment_analysis"},
  "timestamp": "2024-01-01T12:00:00",
  "processing_time_ms": 120.0
}
```

#### 5. Custom Structured Query

**Tool**: `custom_structured_query`

**Purpose**: Execute custom queries with any available schema for maximum flexibility

**Parameters**:
- `prompt` (required): Query or prompt to process
- `schema_name` (required): Schema to use (data_extraction, code_analysis, configuration_task, sentiment_analysis)
- `system_message` (optional): Custom system message
- `model` (optional): OpenAI model to use
- `temperature` (optional): Sampling temperature
- `max_tokens` (optional): Maximum response tokens

**Output**: JSON with structured response according to specified schema

#### 6. List Available Schemas

**Tool**: `list_schemas`

**Purpose**: Get information about all available structured output schemas

**Parameters**: None

**Output**: Formatted text with schema descriptions and usage tips

#### 7. Health Check

**Tool**: `health_check`

**Purpose**: Verify API connectivity and structured output functionality

**Parameters**: None

**Output**: Status message with health information and logging status

## Schema System

### Available Schemas

1. **DataExtraction**: Entities, key facts, summary with confidence scoring
2. **CodeAnalysis**: Language, complexity, issues, strengths, recommendations, metrics
3. **ConfigurationTask**: Task name, priority, steps, prerequisites, validation
4. **SentimentAnalysis**: Overall sentiment, confidence, key phrases, emotions, reasoning

### Schema Validation

All responses are validated against strict JSON schemas using Pydantic models:

- **Type Safety**: Ensures correct data types for all fields
- **Value Constraints**: Enforces ranges, minimums, maximums, and patterns
- **Required Fields**: Guarantees essential fields are present
- **Additional Properties**: Prevents unexpected fields in responses

### Error Handling

Structured error responses with detailed validation information:

```json
{
  "success": false,
  "error_type": "validation_error",
  "error_message": "Input validation failed",
  "validation_errors": [
    {
      "field": "confidence_score",
      "message": "Value must be between 0.0 and 1.0",
      "expected_type": "float",
      "received_value": "1.5"
    }
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

## Development

### Testing

**Run all tests:**
```bash
OPENAI_STRUCTURED_LOG_LEVEL=none uv run python -m pytest
```

**Run specific test suites:**
```bash
# Schema validation tests
OPENAI_STRUCTURED_LOG_LEVEL=none uv run python -m pytest tests/test_schemas.py -v

# Client tests (requires API key mocking)
OPENAI_STRUCTURED_LOG_LEVEL=none uv run python -m pytest tests/test_client.py -v

# Server tests (requires environment setup)
OPENAI_STRUCTURED_LOG_LEVEL=none uv run python -m pytest tests/test_server.py -v
```

### Project Structure

```
src/openai-structured-mcp/
├── pyproject.toml              # Project configuration and dependencies
├── README.md                   # This documentation
├── src/openai_structured_mcp/
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Entry point
│   ├── server.py              # FastMCP server with tools
│   ├── client.py              # OpenAI API client
│   ├── schemas.py             # Pydantic models and validation
│   └── utils/
│       ├── __init__.py        # Utils package
│       └── logging.py         # Logging utilities
└── tests/
    ├── __init__.py            # Test package
    ├── conftest.py            # Pytest configuration and fixtures
    ├── test_schemas.py        # Schema validation tests
    ├── test_client.py         # Client functionality tests
    ├── test_server.py         # Server tool tests
    └── test_logging.py        # Logging utility tests
```

### Architecture

- **FastMCP Integration**: Uses FastMCP framework for MCP protocol implementation
- **OpenAI Client**: Async client with structured output support and comprehensive error handling
- **Schema System**: Pydantic-based validation with JSON Schema generation
- **Logging System**: Multi-level logging with API request/response tracking and data redaction
- **Error Recovery**: Graceful error handling with structured error responses

## Use Cases

### Data Processing Workflows
- Extract structured information from documents, emails, or web content
- Standardize data formats for downstream processing
- Build reliable data pipelines with guaranteed output schemas

### Code Review and Analysis
- Automated code quality assessment
- Identify potential issues and improvement opportunities
- Generate structured feedback for development teams

### Task Management
- Convert high-level requirements into actionable task lists
- Generate implementation plans with clear validation criteria
- Standardize project planning and tracking

### Content Analysis
- Sentiment analysis for customer feedback, reviews, or social media
- Content categorization and emotional analysis
- Brand monitoring and reputation management

## Comparison with Traditional Approaches

### Structured vs Unstructured Outputs

**Traditional Unstructured:**
- Variable response formats
- Requires custom parsing logic
- Error-prone data extraction
- Difficult to validate responses

**OpenAI Structured Outputs:**
- Guaranteed JSON Schema compliance
- No parsing required
- Built-in validation and error handling
- Type-safe data processing

### Benefits of This Implementation

1. **Reliability**: JSON Schema validation ensures consistent response formats
2. **Developer Experience**: Type-safe Pydantic models with IDE support
3. **Error Handling**: Comprehensive error reporting with validation details
4. **Observability**: Detailed logging for debugging and monitoring
5. **Flexibility**: Multiple specialized tools and custom query support
6. **Production Ready**: Comprehensive test suite and error recovery

## Limitations

- Requires OpenAI API with structured output support (GPT-4 models)
- JSON Schema validation adds slight latency overhead
- More rigid than free-form text generation
- Token usage may be higher due to schema constraints

## Future Enhancements

- Additional schema types for specific domains
- Streaming support for large responses
- Schema versioning and migration support
- Integration with other LLM providers
- Performance optimizations and caching

## Contributing

This is an experimental proof-of-concept demonstrating structured output capabilities. Contributions and feedback are welcome for:

- Additional schema types
- Performance improvements
- Error handling enhancements
- Documentation improvements
- Test coverage expansion

## License

This project is part of the AI Code Forge toolkit and follows the same licensing terms.