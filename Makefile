# Self-Documented Makefile see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"
PART 	:= minor

# Put it first so that "make" without argument is like "make help".
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-32s-\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

guard-%: ## Checks that env var is set else exits with non 0 mainly used in CI;
	@if [ -z '${${*}}' ]; then echo 'Environment variable $* not set' && exit 1; fi

# --------------------------------------------------------
# ------- Python package (pip) management commands -------
# --------------------------------------------------------

clean: clean-build clean-pyc clean-test clean-docs  ## remove all build, test, coverage and Python artifacts

clean-build:  ## remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc:  ## remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test:  ## remove test and coverage artifacts
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
	@rm -fr .pytest_cache

clean-docs:  ## remove all doc artifacts
	@rm -fr site

lint:  ## check style with flake8
	@flake8 restricted_fields tests

tox: install-test  ## Run tox test
	@tox

coverage:  ## check code coverage quickly with the default Python
	@coverage run --source restricted_fields -m pytest
	@coverage report -m
	@coverage html
	@$(BROWSER) htmlcov/index.html

build-docs:
	@mkdocs build

github-pages: install-docs
	@mkdocs gh-deploy

servedocs: install-docs build-docs  ## compile the docs watching for changes
	@mkdocs serve

release: dist  ## package and upload a release
	@twine upload dist/*

dist: clean install-deploy  ## builds source and wheel package
	@pip install twine==3.4.1
	@python setup.py sdist bdist_wheel

increase-version: guard-PART  ## Increase project version
	@bump2version $(PART)
	@git switch -c main

install-wheel: clean  ## Install wheel
	@echo "Installing wheel..."
	@pip install wheel

install: requirements.txt install-wheel  ## install the package to the active Python's site-packages
	@pip install -r requirements.txt

install-dev: requirements_dev.txt install-wheel  ## Install local dev packages
	@pip install -e .'[development]' -r requirements_dev.txt

install-docs: install-wheel
	@pip install -e .'[docs]'

install-test: install-wheel
	@pip install -e .'[test]'

install-lint: install-wheel
	@pip install -e .'[lint]'

install-deploy: install-wheel
	@pip install -e .'[deploy]'

test: install-test
	@pytest --basetemp={envtmpdir}

migrations:
	@python manage.py makemigrations

.PHONY: clean clean-test clean-pyc clean-build docs help install-wheel install-docs install-dev install install-lint install-test install-deploy migrations
