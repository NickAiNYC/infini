.PHONY: setup test lint format clean publish conformance certify

setup:
	python -m venv venv
	. venv/bin/activate && pip install -e './cli[dev]'

test:
	python -m pytest cli/tests/ -q

conformance:
	infini conformance tests/conformance/ --engine infini --mock

certify:
	infini certify adapters/hermes --engine infini --mock
	infini certify adapters/openclaw --engine infini --mock

lint:
	python -m py_compile cli/src/infini/*.py || true
	python -m pytest cli/tests/ -q

format:
	@echo "Run: ruff format cli/src/ (if ruff installed)"

clean:
	rm -rf dist/ build/ *.egg-info/ __pycache__/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f *.db

build:
	cd cli && python -m build

check:
	cd cli && python -m twine check dist/*

publish: build check
	cd cli && python -m twine upload dist/*

install-local:
	pip install -e './cli[dev]'

verify: test conformance certify
	@echo "All checks passed."
