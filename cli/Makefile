# Makefile for AI Code Forge CLI

.PHONY: help test test-quick test-unit test-integration coverage clean install dev-install

help: ## Show this help message
	@echo "AI Code Forge CLI - Available Commands:"
	@echo "🎯 9 focused tests (no theater) - validates actual functionality"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Run full test suite with coverage
	@echo "🧪 Running full test suite with coverage..."
	python run_tests.py

test-quick: ## Run quick tests without coverage (fast feedback)  
	@echo "⚡ Running quick tests..."
	python run_tests.py --quick

test-unit: ## Run unit tests only
	@echo "🔧 Running unit tests..."
	python run_tests.py --unit-only

test-integration: ## Run integration tests only
	@echo "🔗 Running integration tests..."
	python run_tests.py --integration-only

coverage: ## Generate and open coverage report
	python run_tests.py
	@echo "📊 Opening coverage report..."
	@python -m webbrowser htmlcov/index.html 2>/dev/null || echo "Coverage report available at htmlcov/index.html"

clean: ## Clean test artifacts and build files
	@echo "🧹 Cleaning test artifacts..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

install: ## Install CLI package
	pip install -e .

dev-install: ## Install CLI package with development dependencies
	pip install -e ".[dev]"

build: ## Build CLI package for distribution
	python -m build

lint: ## Run code linting
	@echo "🔍 Running code linting..."
	python -m flake8 src/ tests/ || echo "⚠️  Install flake8 for linting: pip install flake8"
	python -m black --check src/ tests/ || echo "⚠️  Install black for formatting: pip install black"

format: ## Format code with black
	@echo "✨ Formatting code..."
	python -m black src/ tests/

validate: ## Run all validation checks (tests + linting)
	@echo "🔍 Running full validation..."
	@$(MAKE) lint
	@$(MAKE) test

# Test specific functionality
test-deployment: ## Test template deployment functionality specifically
	python -m pytest tests/test_init_integration.py::TestInitIntegration::test_init_happy_path_full_deployment -v

test-parameters: ## Test parameter substitution functionality
	python -m pytest tests/test_parameter_substitution.py -v

# Development helpers
debug-test: ## Run failing test with pdb debugger
	python -m pytest -v --pdb --tb=long

watch-tests: ## Watch for changes and re-run tests (requires entr)
	@echo "👀 Watching for changes (press Ctrl+C to stop)..."
	find src/ tests/ -name "*.py" | entr -c python run_tests.py --quick