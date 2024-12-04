# export this so that poetry finds itself in the venv and can
# run things from there
VIRTUAL_ENV = .venv
PYTHON_VERSION ?= python3.8
POETRY ?= poetry

.PHONY: all test build clean help lint develop format typecheck lint_all api-docs docs

# settings from .pytest.cfg file
PYTEST_OPTS?=-c .pytest.cfg

all: test docs

help:
	@echo "These are our make targets and what they do."
	@echo ""
	@echo "  help:      Show this helptext"
	@echo ""
	@echo "  install:   Setup repo, install build dependencies"
	@echo ""
	@echo "  test:      [install] + [lint] and run the full suite of tests"
	@echo ""
	@echo "  lint:      [install] and lint code with flake8"
	@echo ""
	@echo "  clean:     Typical cleanup, also scrubs venv"

.PHONY: install
install:
	$(POETRY) install --no-dev --sync

develop:
	$(POETRY) install --sync

lint: develop
	$(POETRY) run tox -e mypy,docs

typecheck: develop
	$(POETRY) run tox -e mypy

lint_all: develop lint

test: develop
	$(POETRY) run tox

%.html: %.yaml
	npx redoc-cli bundle --output $@ --title "Globus Automate APIs" $<

node_modules: package.json
	npm install

api-docs: node_modules docs/actions-api-spec.html docs/flows-api-spec.html

clean:
	rm -rf \
		$(VIRTUAL_ENV) \
		.mypy_cache/ \
		.tox/ \
		*.egg-info/ \
		dist/ \
		docs/build/ \
		htmlcov/ \
		tar-source/ \
		# END rm -rf

	rm -f \
		.coverage \
		*.tar.gz \
		cli_docs.md \
		# END rm -f

	find . -name "*.pyc" -delete


docs: develop
	poetry run typer globus_automate_client/cli/main.py utils docs --name "globus-automate" --output cli_docs.md;
	pandoc --from markdown --to rst -o docs/source/cli_docs.rst cli_docs.md;
	rm cli_docs.md;
	poetry run make --directory=docs html
