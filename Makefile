# Makefile para Python TTS Project
# Facilita execução de comandos comuns de desenvolvimento

.PHONY: help install test test-unit test-integration lint format build-standalone build-exe clean coverage docs run-bot run-standalone setup dev

# Default target
help:
	@echo "🚀 Python TTS - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install      - Install dependencies"
	@echo "  make setup        - Full project setup (venv + deps)"
	@echo "  make dev          - Setup development environment"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-integration - Run integration tests"  
	@echo "  make test-build   - Test system before Windows build"
	@echo "  make coverage     - Generate coverage report"
	@echo ""
	@echo "🔨 Building:"
	@echo "  make build-clean          - Clean Architecture build for Windows (recommended)"
	@echo ""
	@echo "🏃 Running:"
	@echo "  make run-bot      - Run Discord bot"
	@echo "  make run-standalone - Run standalone TTS"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make docs         - Generate documentation"

# Setup commands
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-test.txt

setup:
	@echo "🚀 Setting up Python TTS project..."
	@if [ ! -d ".venv" ]; then python -m venv .venv; fi
	@echo "Activate virtual environment with: source .venv/bin/activate"
	@echo "Then run: make install"

dev: install
	@echo "🔧 Setting up development environment..."
	@if [ ! -f ".env" ]; then cp .env.example .env; echo "📝 Created .env file from example"; fi
	@echo "✅ Development environment ready!"

# Testing commands
test:
	@echo "🧪 Running all tests..."
	python -m pytest tests/ -v

test-unit:
	@echo "🔬 Running unit tests..."
	python -m pytest tests/unit/ -v

test-integration:
	@echo "🔗 Running integration tests..."
	@if [ -d "tests/integration" ]; then python -m pytest tests/integration/ -v; else echo "No integration tests found"; fi

test-build:
	@echo "🧪 Testing system readiness for Windows build..."
	python3 test_integration.py

coverage:
	@echo "📊 Generating coverage report..."
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=xml --cov-report=term

# Build command (Clean Architecture with SOLID principles)
build-clean:
	@echo "🏗️ Building TTS Hotkey with Clean Architecture for Windows..."
	@if command -v pwsh >/dev/null 2>&1; then \
		pwsh -File scripts/build/build_clean_architecture.ps1; \
	else \
		echo "❌ PowerShell not found. Install PowerShell or run script manually:"; \
		echo "   powershell scripts/build/build_clean_architecture.ps1"; \
	fi

# Run commands
run-bot:
	@echo "🤖 Starting Discord bot..."
	python main.py

run-standalone:
	@echo "🎤 Starting standalone TTS..."
	@if [ -f "tts_hotkey_standalone.exe" ]; then \
		./tts_hotkey_standalone.exe; \
	else \
		python app.py; \
	fi

# Development commands
lint:
	@echo "🔍 Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then flake8 src/; fi
	@if command -v pylint >/dev/null 2>&1; then pylint src/; fi
	@if command -v mypy >/dev/null 2>&1; then mypy src/; fi

format:
	@echo "✨ Formatting code..."
	@if command -v black >/dev/null 2>&1; then black src/ tests/; fi
	@if command -v isort >/dev/null 2>&1; then isort src/ tests/; fi

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf build/
	rm -rf dist/
	rm -rf *.spec
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete!"

docs:
	@echo "📚 Opening documentation..."
	@echo "Available documentation:"
	@echo "  - README.md"
	@echo "  - docs/ARCHITECTURE.md"
	@echo "  - docs/TROUBLESHOOTING.md"
	@echo "  - docs/README_STANDALONE.md"
	@echo "  - docs/HOTKEY_SETUP.md"
