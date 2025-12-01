#!/bin/bash

# Python TTS - Script de Automação Principal
# Facilita execução de comandos comuns de desenvolvimento

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para mostrar ajuda
show_help() {
    echo -e "${CYAN}🚀 Python TTS - Available Commands:${NC}"
    echo ""
    echo -e "${YELLOW}📦 Setup & Installation:${NC}"
    echo "  ./scripts.sh install      - Install dependencies"
    echo "  ./scripts.sh setup        - Full project setup (venv + deps)"
    echo "  ./scripts.sh dev          - Setup development environment"
    echo ""
    echo -e "${YELLOW}🧪 Testing:${NC}"
    echo "  ./scripts.sh test         - Run all tests"
    echo "  ./scripts.sh test-unit    - Run unit tests only"
    echo "  ./scripts.sh coverage     - Generate coverage report"
    echo ""
    echo -e "${YELLOW}🔨 Building:${NC}"
    echo "  ./scripts.sh build-exe    - Build standard executable (Windows)"
    echo "  ./scripts.sh build-standalone - Build standalone executable"
    echo "  ./scripts.sh build-configurable - Build configurable version"
    echo ""
    echo -e "${YELLOW}🏃 Running:${NC}"
    echo "  ./scripts.sh run-bot      - Run Discord bot"
    echo "  ./scripts.sh run-standalone - Run standalone TTS"
    echo "  ./scripts.sh run-configurable - Run configurable TTS"
    echo ""
    echo -e "${YELLOW}🔧 Development:${NC}"
    echo "  ./scripts.sh lint         - Run code linting"
    echo "  ./scripts.sh format       - Format code"
    echo "  ./scripts.sh clean        - Clean build artifacts"
    echo "  ./scripts.sh docs         - Show documentation links"
    echo ""
    echo -e "${YELLOW}🧪 Testing Scripts:${NC}"
    echo "  ./scripts.sh test-improvements - Run improvement tests"
    echo "  ./scripts.sh test-config  - Run config GUI test"
    echo "  ./scripts.sh test-discord - Run Discord connection test"
}

# Função para instalar dependências
install_deps() {
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    echo -e "${GREEN}✅ Dependencies installed!${NC}"
}

# Função para setup inicial
setup_project() {
    echo -e "${BLUE}🚀 Setting up Python TTS project...${NC}"
    
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python -m venv .venv
        echo -e "${YELLOW}📝 Virtual environment created!${NC}"
        echo -e "${YELLOW}Activate with: source .venv/bin/activate${NC}"
    else
        echo -e "${GREEN}✅ Virtual environment already exists${NC}"
    fi
}

# Função para setup de desenvolvimento
dev_setup() {
    install_deps
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Created .env file from example${NC}"
    fi
    
    echo -e "${GREEN}✅ Development environment ready!${NC}"
}

# Função para executar testes
run_tests() {
    echo -e "${BLUE}🧪 Running all tests...${NC}"
    python -m pytest tests/ -v
}

# Função para testes unitários
run_unit_tests() {
    echo -e "${BLUE}🔬 Running unit tests...${NC}"
    python -m pytest tests/unit/ -v
}

# Função para coverage
run_coverage() {
    echo -e "${BLUE}📊 Generating coverage report...${NC}"
    python -m pytest tests/ --cov=src --cov-report=html --cov-report=xml --cov-report=term
    echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
}

# Funções para build
build_exe() {
    echo -e "${BLUE}🔨 Building standard executable...${NC}"
    if command -v pwsh >/dev/null 2>&1; then
        pwsh -File scripts/build/build_exe.ps1
    elif command -v powershell >/dev/null 2>&1; then
        powershell scripts/build/build_exe.ps1
    else
        echo -e "${RED}❌ PowerShell not found${NC}"
        echo "Please install PowerShell or run the script manually:"
        echo "   powershell scripts/build/build_exe.ps1"
    fi
}

build_standalone() {
    echo -e "${BLUE}🔨 Building standalone executable...${NC}"
    if command -v pwsh >/dev/null 2>&1; then
        pwsh -File scripts/build/build_standalone.ps1
    elif command -v powershell >/dev/null 2>&1; then
        powershell scripts/build/build_standalone.ps1
    else
        echo -e "${RED}❌ PowerShell not found${NC}"
        echo "Please install PowerShell or run the script manually:"
        echo "   powershell scripts/build/build_standalone.ps1"
    fi
}

build_configurable() {
    echo -e "${BLUE}🔨 Building configurable executable...${NC}"
    if command -v pwsh >/dev/null 2>&1; then
        pwsh -File scripts/build/build_configurable.ps1
    elif command -v powershell >/dev/null 2>&1; then
        powershell scripts/build/build_configurable.ps1
    else
        echo -e "${RED}❌ PowerShell not found${NC}"
        echo "Please install PowerShell or run the script manually:"
        echo "   powershell scripts/build/build_configurable.ps1"
    fi
}

# Funções para executar aplicações
run_bot() {
    echo -e "${BLUE}🤖 Starting Discord bot...${NC}"
    python main.py
}

run_standalone() {
    echo -e "${BLUE}🎤 Starting standalone TTS...${NC}"
    if [ -f "tts_hotkey_standalone.exe" ]; then
        ./tts_hotkey_standalone.exe
    else
        python tts_hotkey_configurable.py
    fi
}

run_configurable() {
    echo -e "${BLUE}⚙️ Starting configurable TTS...${NC}"
    python tts_hotkey_configurable.py
}

# Função para linting
run_lint() {
    echo -e "${BLUE}🔍 Running code linting...${NC}"
    
    if command -v flake8 >/dev/null 2>&1; then
        echo "Running flake8..."
        flake8 src/
    fi
    
    if command -v pylint >/dev/null 2>&1; then
        echo "Running pylint..."
        pylint src/
    fi
    
    if command -v mypy >/dev/null 2>&1; then
        echo "Running mypy..."
        mypy src/
    fi
    
    echo -e "${GREEN}✅ Linting complete!${NC}"
}

# Função para formatação
run_format() {
    echo -e "${BLUE}✨ Formatting code...${NC}"
    
    if command -v black >/dev/null 2>&1; then
        black src/ tests/
    fi
    
    if command -v isort >/dev/null 2>&1; then
        isort src/ tests/
    fi
    
    echo -e "${GREEN}✅ Code formatted!${NC}"
}

# Função para limpeza
clean_project() {
    echo -e "${BLUE}🧹 Cleaning build artifacts...${NC}"
    
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
    
    echo -e "${GREEN}✅ Clean complete!${NC}"
}

# Função para mostrar documentação
show_docs() {
    echo -e "${BLUE}📚 Available documentation:${NC}"
    echo "  - README.md - Main project documentation"
    echo "  - docs/ARCHITECTURE.md - Architecture overview"
    echo "  - docs/TROUBLESHOOTING.md - Troubleshooting guide"
    echo "  - docs/README_STANDALONE.md - Standalone version guide"
    echo "  - docs/HOTKEY_SETUP.md - Hotkey configuration"
    echo "  - docs/SISTEMA_CONEXAO_INTELIGENTE.md - Discord connection system"
}

# Funções para scripts de teste específicos
test_improvements() {
    echo -e "${BLUE}🧪 Running improvement tests...${NC}"
    bash scripts/test/test_improvements.sh
}

test_config() {
    echo -e "${BLUE}🧪 Running config GUI test...${NC}"
    python scripts/test/test_config_gui.py
}

test_discord() {
    echo -e "${BLUE}🧪 Running Discord connection test...${NC}"
    python scripts/test/test_discord_connection.py
}

# Main script logic
case "${1:-help}" in
    "install")
        install_deps
        ;;
    "setup")
        setup_project
        ;;
    "dev")
        dev_setup
        ;;
    "test")
        run_tests
        ;;
    "test-unit")
        run_unit_tests
        ;;
    "coverage")
        run_coverage
        ;;
    "build-exe")
        build_exe
        ;;
    "build-standalone")
        build_standalone
        ;;
    "build-configurable")
        build_configurable
        ;;
    "run-bot")
        run_bot
        ;;
    "run-standalone")
        run_standalone
        ;;
    "run-configurable")
        run_configurable
        ;;
    "lint")
        run_lint
        ;;
    "format")
        run_format
        ;;
    "clean")
        clean_project
        ;;
    "docs")
        show_docs
        ;;
    "test-improvements")
        test_improvements
        ;;
    "test-config")
        test_config
        ;;
    "test-discord")
        test_discord
        ;;
    "help"|*)
        show_help
        ;;
esac