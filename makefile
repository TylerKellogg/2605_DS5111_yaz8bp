VENV_ACTIVATE = . env/bin/activate

default:
	@cat makefile

env:
	python3 -m venv env; $(VENV_ACTIVATE); pip install --upgrade pip

update: env
	$(VENV_ACTIVATE); pip install -r requirements.txt

lint:
	$(VENV_ACTIVATE); pylint bin/ lib/

test: lint
	$(VENV_ACTIVATE); pytest -vv tests

run:
	$(VENV_ACTIVATE); cat mock_transcripts.jsonl | python -u bin/enrich_transcripts.py | python bin/validate_schema.py

test_enrich:
	$(VENV_ACTIVATE); cat mock_transcripts.jsonl | python -u bin/enrich_transcripts.py --model claude | python bin/validate_schema.py

.PHONY: load
load:
	@echo "Initiating Cloud Data Warehouse Synchronizer Node..."
	$(VENV_ACTIVATE); cat data/enriched_transcripts.jsonl | python bin/load_snowflake.py