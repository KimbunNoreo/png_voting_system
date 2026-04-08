PYTHON ?= python

.PHONY: run run-offline-sync test lint check-phase1

run:
	$(PYTHON) manage.py runserver

run-offline-sync:
	$(PYTHON) manage.py run-offline-sync

test:
	$(PYTHON) -m unittest

lint:
	$(PYTHON) -m compileall .

check-phase1:
	$(PYTHON) manage.py check-phase1
