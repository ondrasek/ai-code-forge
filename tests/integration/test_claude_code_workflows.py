"""Integration tests for Claude Code workflow patterns using MCP servers."""

import pytest
import asyncio
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, PerformanceTestMixin
from tests.shared.mock_factories import PerplexityMockFactory, OpenAIMockFactory, GenericMockFactory

# Setup servers with mock keys
with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key", "OPENAI_API_KEY": "test-key"}):
    from perplexity_mcp import server as perplexity_server
    from openai_structured_mcp import server as openai_server


class TestClaudeCodeResearchWorkflows(AsyncTestBase, PerformanceTestMixin):
    """Test research-focused Claude Code workflows."""
    
    def setup_method(self):
        super().setup_method()
        self._init_performance_baselines()
        self.sample_data = GenericMockFactory.create_sample_data()
    
    @pytest.mark.asyncio
    async def test_comprehensive_research_workflow(self):
        """Test comprehensive research workflow using both MCP servers."""
        # Workflow: Research -> Extract -> Analyze -> Synthesize
        
        # Step 1: Initial research
        initial_research = PerplexityMockFactory.create_successful_response(
            content="Machine learning model deployment involves containerization, orchestration, monitoring, and scaling considerations.",
            related_questions=["How to monitor ML models?", "What are scaling strategies?"],
            citations=["MLOps Guide 2024", "Kubernetes ML Patterns"]
        )
        
        # Step 2: Deep research on specific aspects
        deep_research = PerplexityMockFactory.create_successful_response(
            content="Container orchestration for ML models requires resource management, health checks, rolling updates, and traffic routing for A/B testing.",
            related_questions=["How to implement A/B testing?"],
            citations=["Docker ML Best Practices", "Kubernetes Operators"]
        )
        
        # Step 3: Extract structured insights
        extraction_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "entities": ["Machine Learning", "Containerization", "Kubernetes", "A/B Testing"],
                "key_facts": [
                    "ML deployment requires orchestration",
                    "Monitoring is critical for production",
                    "A/B testing enables model comparison"
                ],
                "summary": "ML deployment is a multi-faceted process requiring orchestration, monitoring, and testing infrastructure",
                "confidence_score": 0.94
            }
        )
        
        # Step 4: Generate implementation plan
        implementation_plan = OpenAIMockFactory.create_successful_structured_response(
            data={
                "task_name": "ML Model Deployment Pipeline",
                "priority": "high",
                "steps": [
                    "Containerize ML models with Docker",
                    "Setup Kubernetes orchestration",
                    "Implement health monitoring",
                    "Configure A/B testing framework",
                    "Setup automated scaling"
                ],
                "prerequisites": ["Docker knowledge", "Kubernetes cluster", "ML model artifacts"],
                "estimated_duration": "2-3 sprints",
                "validation_criteria": [
                    "Models deploy without downtime",
                    "Monitoring alerts work correctly",
                    "A/B tests show statistical significance"
                ]
            },
            schema_name="configuration_task"
        )
        
        with patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([initial_research, deep_research])), \
             patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([extraction_response, implementation_plan])):
            
            # Execute workflow
            start_time = asyncio.get_event_loop().time()
            
            # Step 1: Initial research
            initial_result = await perplexity_server.perplexity_search(
                query="machine learning model deployment best practices 2024"
            )
            
            # Step 2: Deep dive research
            deep_result = await perplexity_server.perplexity_deep_research(
                topic="ML model orchestration and scaling",
                focus_areas=["containerization", "kubernetes", "monitoring"],
                time_filter="month"
            )
            
            # Step 3: Extract structured insights
            insights_result = await openai_server.extract_data(
                text="Machine learning deployment involves orchestration and monitoring",
                custom_instructions="Focus on technical requirements and implementation challenges"
            )
            
            # Step 4: Generate actionable plan
            plan_result = await openai_server.create_configuration_task(
                description="Create comprehensive ML deployment pipeline based on research findings"
            )
            
            duration = asyncio.get_event_loop().time() - start_time
            self.record_performance('comprehensive_workflow', duration * 1000)
            
            # Validate workflow results
            assert "deployment involves containerization" in initial_result
            assert "orchestration for ML models" in deep_result
            
            insights_data = self.assert_valid_json_response(insights_result)
            assert "Machine Learning" in insights_data["data"]["entities"]
            assert insights_data["data"]["confidence_score"] > 0.9
            
            plan_data = self.assert_valid_json_response(plan_result)
            assert "ML Model Deployment Pipeline" in plan_data["data"]["task_name"]
            assert len(plan_data["data"]["steps"]) >= 5
            
            # Performance should be reasonable for complex workflow
            self.assert_performance_baseline('batch_operation', duration * 1000)
    
    @pytest.mark.asyncio
    async def test_iterative_refinement_workflow(self):
        """Test iterative refinement workflow with feedback loops."""
        # Simulate iterative development workflow
        
        # Iteration 1: Initial analysis
        initial_analysis = OpenAIMockFactory.create_successful_structured_response(
            data={
                "language": "python",
                "complexity_score": 8,
                "issues": ["High complexity", "No error handling", "Missing documentation"],
                "strengths": ["Clear naming"],
                "recommendations": ["Break down functions", "Add error handling"]
            },
            schema_name="code_analysis"
        )
        
        # Research improvement strategies
        improvement_research = PerplexityMockFactory.create_successful_response(
            content="Python code complexity reduction techniques include function decomposition, early returns, and error handling patterns.",
            related_questions=["What are SOLID principles?", "How to handle errors gracefully?"]
        )
        
        # Iteration 2: Refined analysis after improvements
        refined_analysis = OpenAIMockFactory.create_successful_structured_response(
            data={
                "language": "python",
                "complexity_score": 4,
                "issues": ["Minor style issues"],
                "strengths": ["Clear naming", "Good error handling", "Well documented"],
                "recommendations": ["Consider type hints"]
            },
            schema_name="code_analysis"
        )
        
        with patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([initial_analysis, refined_analysis])), \
             patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([improvement_research])):
            
            # Iteration 1: Analyze current code
            initial_result = await openai_server.analyze_code(
                code=self.sample_data["sample_code"],
                language_hint="python"
            )
            
            initial_data = self.assert_valid_json_response(initial_result)
            complexity_before = initial_data["data"]["complexity_score"]
            issues_before = len(initial_data["data"]["issues"])
            
            # Research improvements based on issues found
            research_result = await perplexity_server.perplexity_search(
                query="Python code complexity reduction error handling best practices"
            )
            
            # Iteration 2: Analyze improved code (simulated)
            refined_result = await openai_server.analyze_code(
                code="# Improved code would be here",
                language_hint="python"
            )
            
            refined_data = self.assert_valid_json_response(refined_result)
            complexity_after = refined_data["data"]["complexity_score"]
            issues_after = len(refined_data["data"]["issues"])
            
            # Validate improvement
            assert complexity_before > complexity_after
            assert issues_before > issues_after
            assert "complexity reduction techniques" in research_result
    
    @pytest.mark.asyncio
    async def test_decision_support_workflow(self):
        """Test decision support workflow for technical choices."""
        # Workflow: Research options -> Analyze trade-offs -> Generate recommendations
        
        # Research different options
        option_research = PerplexityMockFactory.create_successful_response(
            content="Database choices for microservices include PostgreSQL for ACID compliance, MongoDB for flexibility, Redis for caching, and Cassandra for scalability.",
            related_questions=["What are database trade-offs?", "How to choose database?"],
            citations=["Database Architecture Guide", "Microservices Patterns"]
        )
        
        # Analyze trade-offs
        tradeoff_analysis = OpenAIMockFactory.create_successful_structured_response(
            data={
                "entities": ["PostgreSQL", "MongoDB", "Redis", "Cassandra"],
                "key_facts": [
                    "PostgreSQL provides ACID compliance",
                    "MongoDB offers schema flexibility",
                    "Redis excels at caching",
                    "Cassandra scales horizontally"
                ],
                "summary": "Each database serves different architectural needs in microservices",
                "confidence_score": 0.89
            }
        )
        
        # Generate recommendation
        recommendation = OpenAIMockFactory.create_successful_structured_response(
            data={
                "task_name": "Database Selection for Microservices",
                "priority": "high",
                "steps": [
                    "Analyze data consistency requirements",
                    "Evaluate scaling needs",
                    "Consider team expertise",
                    "Prototype with top 2 options",
                    "Make final selection based on tests"
                ],
                "prerequisites": ["Architecture requirements", "Performance benchmarks"],
                "validation_criteria": ["Meets consistency requirements", "Handles expected load"]
            },
            schema_name="configuration_task"
        )
        
        with patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([option_research])), \
             patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([tradeoff_analysis, recommendation])):
            
            # Execute decision support workflow
            
            # Step 1: Research available options
            research_result = await perplexity_server.perplexity_search(
                query="database options microservices architecture 2024 comparison"
            )
            
            # Step 2: Analyze trade-offs
            analysis_result = await openai_server.extract_data(
                text="Database choices include PostgreSQL, MongoDB, Redis, and Cassandra",
                custom_instructions="Extract key characteristics and use cases for each option"
            )
            
            # Step 3: Generate selection process
            recommendation_result = await openai_server.create_configuration_task(
                description="Create systematic process for selecting optimal database for microservices architecture"
            )
            
            # Validate decision support output
            assert "database choices" in research_result.lower()
            
            analysis_data = self.assert_valid_json_response(analysis_result)
            databases = analysis_data["data"]["entities"]
            assert "PostgreSQL" in databases
            assert "MongoDB" in databases
            
            rec_data = self.assert_valid_json_response(recommendation_result)
            assert "Database Selection" in rec_data["data"]["task_name"]
            assert len(rec_data["data"]["steps"]) > 0


class TestClaudeCodeDevelopmentWorkflows(AsyncTestBase):
    """Test development-focused Claude Code workflows."""
    
    def setup_method(self):
        super().setup_method()
        self.sample_data = GenericMockFactory.create_sample_data()
    
    @pytest.mark.asyncio
    async def test_code_review_workflow(self):
        """Test automated code review workflow."""
        # Workflow: Analyze code -> Research best practices -> Generate review
        
        code_analysis = OpenAIMockFactory.create_successful_structured_response(
            data={
                "language": "python",
                "complexity_score": 5,
                "issues": ["Missing type hints", "No docstrings", "Long parameter list"],
                "strengths": ["Clear variable names", "Good error handling"],
                "recommendations": ["Add type annotations", "Break down function parameters"]
            },
            schema_name="code_analysis"
        )
        
        best_practices_research = PerplexityMockFactory.create_successful_response(
            content="Python best practices include type hints for clarity, comprehensive docstrings for documentation, and limiting function parameters to improve readability.",
            related_questions=["How to write good docstrings?", "What are type hint benefits?"]
        )
        
        review_generation = OpenAIMockFactory.create_successful_structured_response(
            data={
                "task_name": "Code Review Improvements",
                "priority": "medium",
                "steps": [
                    "Add type hints to all function parameters",
                    "Write comprehensive docstrings",
                    "Refactor long parameter lists using dataclasses",
                    "Add unit tests for edge cases"
                ],
                "validation_criteria": ["All functions have type hints", "Documentation is complete"]
            },
            schema_name="configuration_task"
        )
        
        with patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([code_analysis, review_generation])), \
             patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([best_practices_research])):
            
            # Execute code review workflow
            
            # Step 1: Analyze the code
            analysis_result = await openai_server.analyze_code(
                code=self.sample_data["sample_code"],
                language_hint="python"
            )
            
            # Step 2: Research relevant best practices
            research_result = await perplexity_server.perplexity_search(
                query="Python code review best practices type hints docstrings 2024"
            )
            
            # Step 3: Generate improvement tasks
            review_result = await openai_server.create_configuration_task(
                description="Generate actionable code review improvements based on analysis"
            )
            
            # Validate code review workflow
            analysis_data = self.assert_valid_json_response(analysis_result)
            assert "Missing type hints" in analysis_data["data"]["issues"]
            
            assert "type hints" in research_result.lower()
            assert "docstrings" in research_result.lower()
            
            review_data = self.assert_valid_json_response(review_result)
            assert "Code Review Improvements" in review_data["data"]["task_name"]
            assert any("type hints" in step.lower() for step in review_data["data"]["steps"])
    
    @pytest.mark.asyncio
    async def test_documentation_generation_workflow(self):
        """Test documentation generation workflow."""
        # Workflow: Analyze code -> Research documentation standards -> Generate docs
        
        code_analysis = OpenAIMockFactory.create_successful_structured_response(
            data={
                "language": "python",
                "functions_count": 3,
                "classes_count": 1,
                "complexity_score": 4,
                "issues": ["Minimal documentation"],
                "strengths": ["Well-structured code", "Clear function purposes"]
            },
            schema_name="code_analysis"
        )
        
        documentation_research = PerplexityMockFactory.create_successful_response(
            content="Python documentation should follow PEP 257 for docstrings, include parameter types and return values, provide usage examples, and maintain consistency across the codebase.",
            related_questions=["What is PEP 257?", "How to document Python APIs?"]
        )
        
        doc_plan = OpenAIMockFactory.create_successful_structured_response(
            data={
                "task_name": "Comprehensive Code Documentation",
                "priority": "medium",
                "steps": [
                    "Add module-level docstring",
                    "Document all public functions with parameters and return types",
                    "Include usage examples in docstrings",
                    "Generate API documentation",
                    "Create user guide with examples"
                ],
                "prerequisites": ["Code analysis complete", "Documentation standards defined"],
                "validation_criteria": ["All public APIs documented", "Examples are tested"]
            },
            schema_name="configuration_task"
        )
        
        with patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([code_analysis, doc_plan])), \
             patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([documentation_research])):
            
            # Execute documentation workflow
            
            # Step 1: Analyze code structure
            analysis_result = await openai_server.analyze_code(
                code=self.sample_data["sample_code"],
                language_hint="python"
            )
            
            # Step 2: Research documentation standards
            standards_result = await perplexity_server.perplexity_search(
                query="Python documentation standards PEP 257 docstring best practices"
            )
            
            # Step 3: Generate documentation plan
            plan_result = await openai_server.create_configuration_task(
                description="Create comprehensive documentation plan for Python codebase"
            )
            
            # Validate documentation workflow
            analysis_data = self.assert_valid_json_response(analysis_result)
            assert analysis_data["data"]["functions_count"] > 0
            
            assert "PEP 257" in standards_result
            assert "docstrings" in standards_result
            
            plan_data = self.assert_valid_json_response(plan_result)
            assert "Documentation" in plan_data["data"]["task_name"]
            assert any("docstring" in step.lower() for step in plan_data["data"]["steps"])
    
    @pytest.mark.asyncio
    async def test_performance_optimization_workflow(self):
        """Test performance optimization workflow."""
        # Workflow: Analyze code -> Research optimization techniques -> Plan improvements
        
        performance_analysis = OpenAIMockFactory.create_successful_structured_response(
            data={
                "language": "python",
                "complexity_score": 7,
                "issues": ["Nested loops", "Repeated calculations", "Memory inefficient"],
                "strengths": ["Readable logic"],
                "recommendations": ["Cache calculations", "Use vectorization", "Optimize data structures"]
            },
            schema_name="code_analysis"
        )
        
        optimization_research = PerplexityMockFactory.create_successful_response(
            content="Python performance optimization techniques include caching with functools.lru_cache, using NumPy for vectorization, choosing efficient data structures, and profiling with cProfile.",
            related_questions=["How to profile Python code?", "What are NumPy benefits?"],
            citations=["Python Performance Guide", "NumPy Documentation"]
        )
        
        optimization_plan = OpenAIMockFactory.create_successful_structured_response(
            data={
                "task_name": "Python Performance Optimization",
                "priority": "high",
                "steps": [
                    "Profile code to identify bottlenecks",
                    "Implement caching for repeated calculations",
                    "Replace loops with NumPy vectorization",
                    "Optimize data structures",
                    "Benchmark improvements"
                ],
                "prerequisites": ["Profiling tools installed", "NumPy available"],
                "validation_criteria": ["Performance improved by >20%", "Memory usage reduced"]
            },
            schema_name="configuration_task"
        )
        
        with patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([performance_analysis, optimization_plan])), \
             patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([optimization_research])):
            
            # Execute performance optimization workflow
            
            # Step 1: Analyze code for performance issues
            analysis_result = await openai_server.analyze_code(
                code=self.sample_data["sample_code"],
                language_hint="python"
            )
            
            # Step 2: Research optimization techniques
            research_result = await perplexity_server.perplexity_deep_research(
                topic="Python performance optimization",
                focus_areas=["caching", "vectorization", "profiling"],
                max_tokens=1000
            )
            
            # Step 3: Create optimization plan
            plan_result = await openai_server.create_configuration_task(
                description="Create systematic performance optimization plan based on code analysis"
            )
            
            # Validate optimization workflow
            analysis_data = self.assert_valid_json_response(analysis_result)
            assert "Nested loops" in analysis_data["data"]["issues"]
            assert "Cache calculations" in analysis_data["data"]["recommendations"]
            
            assert "caching" in research_result.lower()
            assert "vectorization" in research_result.lower()
            
            plan_data = self.assert_valid_json_response(plan_result)
            assert "Performance Optimization" in plan_data["data"]["task_name"]
            assert any("profile" in step.lower() for step in plan_data["data"]["steps"])
