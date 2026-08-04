"""Unit tests for the OOP strategy-pattern enrichment components."""
import sys
import io
import os
import json
import pytest

from lib.enrichment import (
    ClaudeEnricher,
    GeminiEnricher,
    TranscriptEnricher,
    EnrichmentEngine,
    main,
)


def test_claude_enricher_strips_timestamps():
    """ClaudeEnricher is a pure transform: no network, no env var, no patching."""
    enricher = ClaudeEnricher()
    result = enricher.enrich("ds5111_v001", "00:01 Welcome back to class! 00:45 Next up.")

    assert result["video_id"] == "ds5111_v001"
    assert "00:01" not in result["cleaned_text"]
    assert result["cleaned_text"].startswith("Welcome back to class!")
    assert result["tech_terms"] == []

class FakeEnricher(TranscriptEnricher):  # pylint: disable=too-few-public-methods
    """Provider-free strategy proving the engine needs no SDK to be tested."""

    def enrich(self, video_id: str, raw_text: str) -> dict:
        return {"video_id": video_id, "cleaned_text": raw_text.upper()}


def test_engine_streams_and_survives_bad_rows(monkeypatch, capsys):
    """Engine emits good records and skips corrupt ones without aborting."""
    rows = [
        json.dumps({"video_id": "v1", "raw_text": "hello"}),
        "{not valid json",
        json.dumps({"video_id": "v2"}),
    ]
    monkeypatch.setattr(sys, "stdin", io.StringIO("\n".join(rows) + "\n"))

    EnrichmentEngine(FakeEnricher()).run_stream()

    out = capsys.readouterr().out.strip().split("\n")
    assert len(out) == 1
    assert json.loads(out[0]) == {"video_id": "v1", "cleaned_text": "HELLO"}


def test_main_claude_path_streams_records(monkeypatch, capsys):
    """--model claude runs end to end with no API key and no SDK patching."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    row = {"video_id": "ds5111_v001", "raw_text": "00:01 Testing the mock stub."}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(row) + "\n"))

    main(["--model", "claude"])

    out = capsys.readouterr().out.strip().split("\n")
    assert len(out) == 1
    parsed = json.loads(out[0])
    assert parsed["video_id"] == "ds5111_v001"
    assert parsed["cleaned_text"] == "Testing the mock stub."

@pytest.mark.skipif(
    os.getenv("GEMINI_API_KEY") is None,
    reason="GeminiEnricher construction requires a live API key in the environment",
)
def test_gemini_enricher_constructs_with_key():
    """GeminiEnricher initializes when credentials are present (skipped in CI)."""
    enricher = GeminiEnricher()
    assert enricher.model == "gemini-2.5-flash"


@pytest.mark.xfail(
    reason="ClaudeEnricher is a stub: it does not yet extract tech terms",
    strict=True,
)
def test_claude_enricher_extracts_tech_terms():
    """Documents a known stub limitation; will flip to passing when Claude goes live."""
    enricher = ClaudeEnricher()
    result = enricher.enrich("ds5111_v001", "00:01 We discussed Kubernetes today.")
    assert "Kubernetes" in result["tech_terms"]