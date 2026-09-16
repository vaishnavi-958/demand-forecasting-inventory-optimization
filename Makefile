.PHONY: setup sample pipeline forecasts dashboard-data test lint web

PYTHON ?= python3

setup:
	$(PYTHON) -m pip install -r requirements.txt

sample:
	$(PYTHON) scripts/generate_sample_data.py

pipeline:
	$(PYTHON) scripts/run_pipeline.py

forecasts:
	$(PYTHON) scripts/run_forecasts.py

dashboard-data:
	$(PYTHON) scripts/generate_dashboard_data.py

db:
	$(PYTHON) scripts/setup_database.py

test:
	$(PYTHON) -m pytest tests -q

web:
	cd web && npm run dev -- --hostname 0.0.0.0 --port 43125

all: sample pipeline dashboard-data test
