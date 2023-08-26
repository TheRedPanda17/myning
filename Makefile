play:
	@./run.sh

dev:
	@./dev.sh

migrate:
	python migrate.py $(id)

venv:
	pyenv install 3.10 --skip-existing
	pyenv virtualenv -f 3.10 myning
	pyenv local myning
	pip install -r requirements.txt

venv-dev:
	pyenv install 3.10 --skip-existing
	pyenv virtualenv -f 3.10 myning-dev
	pyenv local dev-myning
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

deps-install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

deps-compile:
	pip-compile --no-emit-index-url --no-emit-trusted-host requirements.in
	pip-compile --no-emit-index-url --no-emit-trusted-host requirements-dev.in
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint: isort black
	@true

isort:
	isort . --check --diff

black:
	black . --check

test:
	pytest
