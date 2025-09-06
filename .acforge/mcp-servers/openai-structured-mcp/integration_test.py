#!/usr/bin/env python3
"""Integration test demonstrating OpenAI structured output MCP server functionality.

This script demonstrates the core capabilities without requiring a full MCP client.
It tests the schema validation system and shows how structured outputs work.
"""

import asyncio
import json
from openai_structured_mcp.schemas import (
    validate_structured_data, 
    get_json_schema, 
    SCHEMA_REGISTRY
)
from openai_structured_mcp.client import OpenAIStructuredClient


async def test_schema_validation():
    """Test the schema validation system."""
    print("=== Testing Schema Validation System ===")
    
    # Test data extraction schema
    print("\n1. Testing DataExtraction schema...")
    data_extraction_example = {
        "entities": ["OpenAI", "GPT-4", "Python"],
        "key_facts": [
            "GPT-4 supports structured outputs",
            "JSON Schema validation ensures consistency"
        ],
        "summary": "OpenAI's GPT-4 provides structured output capabilities using JSON Schema validation.",
        "confidence_score": 0.95
    }
    
    result = validate_structured_data(data_extraction_example, "data_extraction")
    if hasattr(result, 'entities'):  # Valid result
        print(f"  ✅ Valid - Entities: {result.entities}")
        print(f"  ✅ Valid - Confidence: {result.confidence_score}")
    else:
        print(f"  ❌ Validation errors: {result}")
    
    # Test code analysis schema
    print("\n2. Testing CodeAnalysis schema...")
    code_analysis_example = {
        "language": "python",
        "complexity_score": 6,
        "issues": ["Missing docstrings", "Long function"],
        "strengths": ["Good variable names", "Proper error handling"],
        "recommendations": ["Add type hints", "Split complex function"],
        "functions_count": 3,
        "lines_of_code": 45
    }
    
    result = validate_structured_data(code_analysis_example, "code_analysis")
    if hasattr(result, 'language'):
        print(f"  ✅ Valid - Language: {result.language}")
        print(f"  ✅ Valid - Complexity: {result.complexity_score}")
    else:
        print(f"  ❌ Validation errors: {result}")
    
    # Test invalid data
    print("\n3. Testing invalid data (should fail)...")
    invalid_data = {
        "entities": ["Test"],
        "key_facts": [],  # Invalid: min_length=1
        "summary": "Too short",  # Invalid: min_length=10
        "confidence_score": 1.5  # Invalid: max=1.0
    }
    
    result = validate_structured_data(invalid_data, "data_extraction")
    if isinstance(result, list):
        print(f"  ✅ Validation correctly failed with {len(result)} errors")
        for error in result[:2]:  # Show first 2 errors
            print(f"    - {error.field}: {error.message}")
    else:
        print(f"  ❌ Should have failed validation")


def test_json_schema_generation():
    """Test JSON schema generation."""
    print("\n=== Testing JSON Schema Generation ===")
    
    for schema_name in SCHEMA_REGISTRY:
        try:
            schema = get_json_schema(schema_name)
            properties_count = len(schema.get("properties", {}))
            required_count = len(schema.get("required", []))
            print(f"  ✅ {schema_name}: {properties_count} properties, {required_count} required")
        except Exception as e:
            print(f"  ❌ {schema_name}: Failed to generate schema - {e}")


async def test_client_initialization():
    """Test client initialization without making API calls."""
    print("\n=== Testing Client Initialization ===")
    
    try:
        # Test without API key (should fail)
        import os
        original_key = os.environ.get("OPENAI_API_KEY")
        if original_key:
            del os.environ["OPENAI_API_KEY"]
        
        try:
            client = OpenAIStructuredClient()
            print("  ❌ Should have failed without API key")
        except ValueError as e:
            print(f"  ✅ Correctly failed without API key: {str(e)[:50]}...")
        
        # Test with API key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
        else:
            os.environ["OPENAI_API_KEY"] = "test-key-for-demo"  # For demo only
        
        client = OpenAIStructuredClient()
        schemas = client.get_available_schemas()
        print(f"  ✅ Client initialized with {len(schemas)} available schemas")
        
        # Clean up
        if not original_key:
            del os.environ["OPENAI_API_KEY"]
        
    except Exception as e:
        print(f"  ❌ Client initialization failed: {e}")


def demonstrate_structured_output_benefits():
    """Demonstrate the benefits of structured outputs."""
    print("\n=== Structured Output Benefits Demo ===")
    
    print("\n📊 Traditional Unstructured Response:")
    unstructured_example = '''
    The code appears to be written in Python and has moderate complexity. 
    There are some issues like missing docstrings and no type hints. 
    However, it has good variable names and proper error handling. 
    I'd recommend adding documentation and type annotations. 
    The code has about 45 lines and 3 functions.
    '''
    print(f"  Raw text: {unstructured_example.strip()}")
    print("  ❌ Requires custom parsing")
    print("  ❌ Inconsistent format")
    print("  ❌ No type safety")
    print("  ❌ Error-prone extraction")
    
    print("\n🎯 Structured Response with JSON Schema:")
    structured_example = {
        "language": "python",
        "complexity_score": 4,
        "issues": ["Missing docstrings", "No type hints"],
        "strengths": ["Good variable names", "Proper error handling"],
        "recommendations": ["Add documentation", "Include type annotations"],
        "functions_count": 3,
        "lines_of_code": 45
    }
    print(f"  JSON: {json.dumps(structured_example, indent=2)}")
    print("  ✅ Guaranteed format")
    print("  ✅ Type-safe access")
    print("  ✅ No parsing required")
    print("  ✅ Validation built-in")


async def main():
    """Run all integration tests."""
    print("🚀 OpenAI Structured Output MCP Server - Integration Test")
    print("==========================================================")
    
    # Test schema validation system
    await test_schema_validation()
    
    # Test JSON schema generation
    test_json_schema_generation()
    
    # Test client initialization
    await test_client_initialization()
    
    # Demonstrate benefits
    demonstrate_structured_output_benefits()
    
    print("\n✨ Integration test completed!")
    print("\nNext steps:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Run: uv run openai-structured-mcp")
    print("3. Use with MCP-compatible clients like Claude Desktop")


if __name__ == "__main__":
    asyncio.run(main())