.PHONY: help install install-dev test test-quick lint format type-check clean build docs example-docs build-all-docs serve-docs serve-examples ci-test prepare-release generate-badges

help:
	@echo "Available commands:"
	@echo "  install         - Install package"
	@echo "  install-dev     - Install package in development mode"
	@echo "  test            - Run tests with coverage"
	@echo "  test-quick      - Run tests quickly"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"
	@echo "  type-check      - Run type checking"
	@echo "  clean           - Clean build artifacts"
	@echo "  build           - Build package"
	@echo "  docs            - Build documentation"
	@echo "  example-docs    - Build example documentation"
	@echo "  build-all-docs  - Build all documentation"
	@echo "  serve-docs      - Serve documentation locally"
	@echo "  serve-examples  - Serve examples locally"
	@echo "  ci-test         - Run full CI test suite"
	@echo "  prepare-release - Prepare for release"
	@echo "  generate-badges - Generate coverage badge"

install:
	pip install .

install-dev:
	pip install -e .[dev]

test:
	pytest --cov=pytest_jsonschema_snapshot --cov-report=xml --cov-report=html --cov-report=term-missing

test-quick:
	pytest --tb=short

lint:
	flake8 pytest_jsonschema_snapshot/ tests/
	black --check pytest_jsonschema_snapshot/ tests/
	isort --check-only pytest_jsonschema_snapshot/ tests/

format:
	black pytest_jsonschema_snapshot/ tests/
	isort pytest_jsonschema_snapshot/ tests/

type-check:
	mypy pytest_jsonschema_snapshot/

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf docs/_build/ examples/docs/_build/
	rm -rf htmlcov/ .coverage coverage.xml coverage.svg
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

build-install:
	$(MAKE) build
	$(MAKE) install

reinstall:
	./reinstall_plugin.sh

docs:
	cd docs && sphinx-build -b html source _build/html

serve-docs:
	cd docs/_build/html && python -m http.server 8000

# CI simulation
ci-test:
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	$(MAKE) build
	$(MAKE) build-all-docs

# Release preparation
prepare-release:
	$(MAKE) clean
	$(MAKE) ci-test
	$(MAKE) build
	twine check dist/*

# Badge generation
generate-badges:
	pytest --tb=short > test_results.txt 2>&1 || true
	pip install coverage-badge
	coverage-badge -o coverage.svg

all: format lint type-check test
