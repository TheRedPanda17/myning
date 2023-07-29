play:
	@./run.sh

venv:
	pyenv install 3.10.2 --skip-existing
	pyenv virtualenv -f 3.10.2 myning
	pyenv local myning
	pip install -r requirements.txt

dev-venv:
	pyenv install 3.10.2 --skip-existing
	pyenv virtualenv -f 3.10.2 dev-myning
	pyenv local dev-myning
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev:
	python -m pdb -c continue dev.py

clean:
	@rm -rf .data

restart:
	@make clean
	@make play

lint: isort black
	@true

migrate:
	python migrate.py $(id)