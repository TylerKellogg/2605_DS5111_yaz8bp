"""Unit tests for the OOP strategy-pattern enrichment components."""
from bin.enrich_transcripts import ClaudeEnricher


def test_claude_enricher_strips_timestamps():
    """ClaudeEnricher is a pure transform: no network, no env var, no patching."""
    enricher = ClaudeEnricher()
    result = enricher.enrich("ds5111_v001", "00:01 Welcome back to class! 00:45 Next up.")

    assert result["video_id"] == "ds5111_v001"
    assert "00:01" not in result["cleaned_text"]
    assert result["cleaned_text"].startswith("Welcome back to class!")
    assert result["tech_terms"] == []
