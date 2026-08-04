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


DOCKER_IMAGE = tylerkellogg/ds5111-pipeline:latest

.PHONY: docker_check docker_build docker_smoke docker_shortcircuit docker_run docker_push docker_cleanroom

docker_check:
	docker ps

docker_build:
	docker build -t $(DOCKER_IMAGE) .

docker_smoke:
	cat data/youtube_ids.txt | docker run -i $(DOCKER_IMAGE)

docker_shortcircuit:
	cat data/youtube_ids.txt | docker run -i --env-file .env $(DOCKER_IMAGE) sh -c "python bin/clean_ids.py | python bin/extract_transcripts.py"

docker_run:
	cat data/youtube_ids.txt | docker run -i --env-file .env $(DOCKER_IMAGE)

docker_push:
	docker push $(DOCKER_IMAGE)

docker_cleanroom:
	docker rm -f $$(docker ps -aq) || true
	docker rmi $(DOCKER_IMAGE)
	docker images
	cat data/youtube_ids.txt | docker run -i --env-file .env $(DOCKER_IMAGE)