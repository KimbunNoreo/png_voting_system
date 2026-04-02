PYTHON ?= python

run:
	$(PYTHON) manage.py runserver

test:
	pytest

lint:
	python -m compileall .

migrate:
	$(PYTHON) manage.py migrate

rotate-keys:
	$(PYTHON) scripts/rotate_keys.py

staged-rollout:
	$(PYTHON) scripts/staged_rollout_switch.py
