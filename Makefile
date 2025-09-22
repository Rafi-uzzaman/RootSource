PY=python3
PIP=pip
APP=backend:app
HOST?=0.0.0.0
PORT?=8000

.PHONY: venv install dev start test fmt lint clean

venv:
	$(PY) -m venv .venv
	. .venv/bin/activate

install:
	$(PIP) install -r requirements.txt

dev:
	uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

start:
	gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b $(HOST):$(PORT) $(APP)

test:
	pytest -q

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache dist build
