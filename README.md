# 2605_DS5111_yaz8bp

YouTube transcript pipeline: clean IDs, extract transcripts, enrich via LLM, validate against a schema contract.

## Structure

| Path | Purpose |
| --- | --- |
| `bin/` | Executable entry points and VM bootstrap scripts |
| `lib/` | Importable modules (`enrichment.py`: strategy-pattern LLM enrichment) |
| `tests/` | Pytest suite: unit, parametrized, skipif, xfail |
| `.github/workflows/` | CI: parallel lint/test jobs, Python version matrix, all via `make` |

## Pipeline

Each stage reads stdin, writes JSONL to stdout; diagnostics go to `logs/`, never stdout.

    cat ids | bin/clean_ids.py | bin/extract_transcripts.py | bin/enrich_transcripts.py | bin/validate_schema.py

## Environment

| Variable | Used by |
| --- | --- |
| `WEBSHARE_USER` / `WEBSHARE_PASSWORD` | `extract_transcripts.py` (proxy for cloud IPs) |
| `GEMINI_API_KEY` | `GeminiEnricher` only; `--model claude` needs no credentials |

Put credentials in `.env` at repo root (gitignored).

## Setup

    git clone git@github.com:TylerKellogg/2605_DS5111_yaz8bp.git && cd 2605_DS5111_yaz8bp
    make update      # venv + dependencies
    make test        # lint + full suite, offline-safe

`make` with no target lists all lifecycle commands: `env`, `update`, `lint`, `test`, `run`, `test_enrich`.
