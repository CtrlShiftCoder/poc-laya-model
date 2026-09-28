.PHONY: help setup install test lint format clean serve poc1 poc2 report docker-up docker-down

help:
	@echo "Comandos disponibles:"
	@echo "  make setup        - Configura el entorno (uv + instala deps)"
	@echo "  make install      - Instala dependencias"
	@echo "  make test         - Ejecuta tests"
	@echo "  make lint         - Verifica código con ruff"
	@echo "  make format       - Formatea código con ruff"
	@echo "  make serve        - Inicia laya-serve (puerto 8000)"
	@echo "  make poc1         - Ejecuta PoC 1: Benchmark offline"
	@echo "  make poc2         - Ejecuta PoC 2: Triage de tickets"
	@echo "  make report       - Genera reportes agregados"
	@echo "  make docker-up    - Inicia servicios Docker"
	@echo "  make docker-down  - Detiene servicios Docker"
	@echo "  make clean        - Limpia archivos generados"

setup:
	@echo "Instalando uv si no existe..."
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "Creando entorno virtual..."
	uv venv --python 3.11
	@echo "Instalando dependencias..."
	uv pip install -e ".[dev]"
	@echo "✓ Setup completo"

install:
	uv pip install -e ".[dev]"

test:
	uv run pytest

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

serve:
	@echo "Iniciando laya-serve en puerto 8000..."
	uv run python -m laya.serve --host 0.0.0.0 --port 8000

poc1:
	@echo "Ejecutando PoC 1: Benchmark offline..."
	uv run python -m src.poc1_benchmark.run

poc2:
	@echo "Ejecutando PoC 2: Triage de tickets..."
	uv run python -m src.poc2_triage.run

report:
	@echo "Generando reporte agregado..."
	uv run python -m src.reporting.generate_report

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
