TEST_FLAGS = --cov=src
TEST_PATH = tests

.PHONY: install
install: requirements.txt
	poetry install $(POETRY_EXTRA)

poetry.lock: pyproject.toml
	poetry lock

requirements.txt: poetry.lock
	poetry install $(POETRY_EXTRA)
	poetry export --without-hashes -f requirements.txt -o $@
