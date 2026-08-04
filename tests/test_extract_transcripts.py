"""Isolated tests for the transcript extraction pipeline stage."""
import sys
import io
import json
import pytest
from youtube_transcript_api import YouTubeTranscriptApi

from bin.extract_transcripts import main


class MockTranscriptContainer:
    """Mimics the .to_raw_data() array output return schema"""
    def to_raw_data(self):
        return [
            {"start": 10.5, "text": "Automated container tracking loop text entry."}
        ]


def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):
    """Verifies main() processes IDs from stdin and emits JSONL without network access."""
    def stubbed_fetch_route(self, video_id):
        return MockTranscriptContainer()
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    mock_input_stream = io.StringIO("fake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    main()

    captured_output = capsys.readouterr()
    stdout_lines = captured_output.out.strip().split("\n")

    assert len(stdout_lines) == 1, "The pipeline loop should emit exactly one row per valid input ID."

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed_json_line["raw_text"]


def test_extract_transcripts_handles_unfetchable_id(monkeypatch, capsys):
    """An un-fetchable ID is logged and skipped without crashing or emitting a row."""
    def failing_fetch_route(self, video_id):
        raise RuntimeError("simulated transcript lookup failure")
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", failing_fetch_route)

    monkeypatch.setattr(sys, "stdin", io.StringIO("unfetchable_id\n"))

    main()

    assert capsys.readouterr().out == "", "No JSONL row should be emitted for a failed fetch."


def test_extract_transcripts_skips_blank_lines(monkeypatch, capsys):
    """Blank input lines are skipped; valid IDs around them still emit rows."""
    def stubbed_fetch_route(self, video_id):
        return MockTranscriptContainer()
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    monkeypatch.setattr(sys, "stdin", io.StringIO("\n   \nfake_video_999\n"))

    main()

    stdout_lines = capsys.readouterr().out.strip().split("\n")
    assert len(stdout_lines) == 1, "Blank lines should not produce output rows."
