.PHONY: help setup install test coverage lint format clean run docker-build docker-run dev-server

help:
	@echo "SafeHouse Development Commands"
	@echo "==============================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Set up development environment"
	@echo "  make install        - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev-server     - Run development server"
	@echo "  make run            - Run production server"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run tests"
	@echo "  make coverage       - Run tests with coverage report"
	@echo "  make lint           - Lint code (flake8)"
	@echo "  make format         - Format code (black, isort)"
	@echo "  make type-check     - Type checking (mypy)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make docker-dev     - Run Docker for development"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove build artifacts and cache"
	@echo ""

setup:
	python setup.py

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=. --cov-report=html --cov-report=term

lint:
	flake8 app.py sh_engine.py config.py tests/

format:
	black app.py sh_engine.py config.py tests/ setup.py
	isort app.py sh_engine.py config.py tests/ setup.py

type-check:
	mypy app.py sh_engine.py config.py --ignore-missing-imports

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

dev-server:
	FLASK_ENV=development FLASK_DEBUG=1 python app.py

run:
	gunicorn app:app --bind 0.0.0.0:5000 --workers 4 --timeout 120

docker-build:
	docker build -t safehouse:latest .

docker-run:
	docker run -p 5000:5000 \
		-e VT_API_KEY=${VT_API_KEY} \
		-e URLSCAN_KEY=${URLSCAN_KEY} \
		-e GROQ_KEY=${GROQ_KEY} \
		safehouse:latest

docker-dev:
	docker-compose up

.DEFAULT_GOAL := help
