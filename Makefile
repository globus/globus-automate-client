# export this so that poetry finds itself in the venv and can
# run things from there
export VIRTUAL_ENV = .venv
PYTHON_VERSION ?= python3.6
POETRY ?= $(VIRTUAL_ENV)/bin/poetry

.PHONY: lock test build clean help lint develop format typecheck lint_all

# settings from .pytest.cfg file
PYTEST_OPTS?=-c .pytest.cfg

help:
	@echo "These are our make targets and what they do."
	@echo ""
	@echo "  help:      Show this helptext"
	@echo ""
	@echo "  install:   Setup repo, install build dependencies"
	@echo "             touch a flagfile used by other make targets"
	@echo ""
	@echo "  test:      [install] + [lint] and run the full suite of tests"
	@echo ""
	@echo "  lint:      [install] and lint code with flake8"
	@echo ""
	@echo "  clean:     Typical cleanup, also scrubs venv"

poetry.lock: pyproject.toml $(VIRTUAL_ENV)
	$(POETRY) lock

lock: poetry.lock

$(VIRTUAL_ENV):
	virtualenv --python=$(PYTHON_VERSION) $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python -m pip install poetry

install: $(VIRTUAL_ENV) poetry.lock
	$(POETRY) install --no-dev

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV)
	$(POETRY) install

develop: $(VIRTUAL_ENV)/bin/py.test

requirements.txt: poetry.lock
	$(POETRY) run pip freeze > $@

# linting is flake8
lint: develop
	$(POETRY) run flake8 globus

# formatting is black
format: develop
	$(POETRY) run black -q globus tests

# typecheck with mypy
typecheck: develop
	$(POETRY) run mypy globus

lint_all: develop format lint typecheck

test: lint_all
	$(POETRY) run pytest --verbose $(PYTEST_OPTS)

clean:
	rm -rf $(VIRTUAL_ENV)
	rm -rf .make_install_flag
	find . -name "*.pyc" -delete
	rm -rf *.egg-info
	rm -f *.tar.gz
	rm -rf tar-source
