# export this so that poetry finds itself in the venv and can
# run things from there
VIRTUAL_ENV = .venv
PYTHON_VERSION ?= python3.6
POETRY ?= poetry

.PHONY: lock test build clean help lint develop format typecheck lint_all api-docs

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

poetry.lock: pyproject.toml
	$(POETRY) lock

lock: poetry.lock

install: poetry.lock
	$(POETRY) install --no-dev

develop: poetry.lock
	$(POETRY) install

requirements.txt: poetry.lock
	$(POETRY) run pip freeze > $@

# linting is flake8
lint: develop
	$(POETRY) run flake8 globus_automate_client

# formatting is black
format: develop
	$(POETRY) run black -q globus_automate_client tests

# typecheck with mypy
typecheck: develop
	$(POETRY) run mypy globus_automate_client

lint_all: develop format lint typecheck

test: lint_all
	$(POETRY) run pytest --verbose $(PYTEST_OPTS)

%.html: %.yaml
	npx redoc-cli bundle --output $@ --title "Globus Automate APIs" $<

node_modules: package.json
	npm install

api-docs: node_modules docs/actions-api-spec.html docs/flows-api-spec.html

clean:
	rm -rf $(VIRTUAL_ENV)
	rm -rf .make_install_flag
	find . -name "*.pyc" -delete
	rm -rf *.egg-info
	rm -f *.tar.gz
	rm -rf tar-source
	rm -rf dist
