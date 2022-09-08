.PHONY: clean-pyc clean-build docs clean lint test coverage docs dist tag release-check

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "dist - package"
	@echo "tag - set a tag with the current version number"
	@echo "release-check - check release tag"


dev-setup: venv
	npm install -g elm-live
	npm install elm-test -g
	npm install -g cypress
	venv/bin/python manage.py migrate

clean: clean-build clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-docs:
	rm -f docs/tri*.rst

lint:
	tox -e lint

test:
	tox --skip-missing-interpreters

coverage:
	tox -e coverage

docs:
	tox -e docs

dist: clean
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	ls -l dist

tag:
	python3 setup.py tag

release-check:
	python3 setup.py release_check

venv:
	`which python3` -m venv venv
	venv/bin/pip install -r requirements.txt


i18n:
	./manage.py makemessages --locale sv --ignore=venv --no-location
	./manage.py compilemessages --ignore=venv

collect-static:
	./manage.py collectstatic --no-input


decoders:
	python3 generate_decoders.py

migrate-deploy:
	env
	./manage.py migrate --noinput

predeploy: migrate-deploy collect-static i18n

