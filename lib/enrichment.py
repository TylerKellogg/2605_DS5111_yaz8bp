#!/usr/bin/env python3
"""Enrich raw YouTube transcripts from stdin using a pluggable LLM provider.

Reads JSON Lines records, delegates enrichment to a selected strategy under a strict
response schema, and emits schema-compliant enriched records to stdout.
"""
import sys
import os
import re
import json
import argparse
import logging
from abc import ABC, abstractmethod

from dotenv import load_dotenv




# Load environmental configurations from local workspace files
load_dotenv()

# Audit logging framework tracking pipeline telemetry
logging.basicConfig(
    filename='logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# =====================================================================
# 1. THE ENRICHMENT CONTRACT (Interface)
# =====================================================================
class TranscriptEnricher(ABC):  # pylint: disable=too-few-public-methods
    """Invariant contract every enrichment provider must satisfy."""

    @abstractmethod
    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Accept a video id and raw transcript, return an enriched record dict."""


# 2. STRATEGY A: THE CLAUDE ENRICHER (Mock Stub — No Network)
# =====================================================================
class ClaudeEnricher(TranscriptEnricher):  # pylint: disable=too-few-public-methods
    """Deterministic stand-in for a live Claude enrichment call."""

    def __init__(self, model: str = "claude-mock-v1"):
        self.model = model

    def enrich(self, video_id: str, raw_text: str) -> dict:
        # Local stand-in for the provider's timestamp-stripping instruction.
        cleaned = re.sub(r"\b\d{1,2}:\d{2}\b", "", raw_text)
        return {
            "video_id": video_id,
            "cleaned_text": " ".join(cleaned.split()),
            "tech_terms": [],
            "book_names": [],
        }

# =====================================================================
# 3. STRATEGY B: THE LIVE GEMINI ENRICHER (Structured JSON Output)
# =====================================================================
class GeminiEnricher(TranscriptEnricher):  # pylint: disable=too-few-public-methods
    """Live enrichment via the Gemini API under a strict response schema."""

    RESPONSE_SCHEMA = {
        "type": "OBJECT",
        "properties": {
            "video_id": {"type": "STRING"},
            "cleaned_text": {"type": "STRING"},
            "tech_terms": {"type": "ARRAY", "items": {"type": "STRING"}},
            "book_names": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["video_id", "cleaned_text"],
    }

    def __init__(self, model: str = "gemini-2.5-flash"):
        from google import genai  # pylint: disable=import-outside-toplevel
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not found in environment.")
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def enrich(self, video_id: str, raw_text: str) -> dict:
        from google.genai import types  # pylint: disable=import-outside-toplevel
        prompt = (
            f"You are an elite data engineer. Clean this transcript text for "
            f"video_id '{video_id}'.\n"
            "1. Strip all timestamps and duration codes.\n"
            "2. Extract technical architecture terms and books."
        )
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{prompt}\n\nTRANSCRIPT:\n{raw_text}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=self.RESPONSE_SCHEMA,
                ),
            )
            return json.loads(response.text)
        # Wrap provider faults in a neutral error so the engine stays provider-agnostic.
        except Exception as e:  # pylint: disable=broad-exception-caught
            raise RuntimeError(f"Gemini enrichment failed for {video_id}: {e}") from e

# =====================================================================
# 4. THE INVARIANT PIPELINE CONTEXT (The Streaming Engine)
# =====================================================================
class EnrichmentEngine:  # pylint: disable=too-few-public-methods
    """Provider-agnostic stream runner: stdin JSONL -> enriched JSONL on stdout."""

    def __init__(self, strategy: TranscriptEnricher):
        self.strategy = strategy

    def run_stream(self):
        """Enrich each stdin record, emitting results and surviving bad rows."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
                video_id = payload["video_id"]
                raw_text = payload["raw_text"]
            # One corrupt row must not kill the stream --- log and continue.
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logging.error("Failed to parse incoming JSON payload row: %s", e)
                continue

            logging.info("Orchestrating enrichment for video: %s", video_id)

            try:
                enriched = self.strategy.enrich(video_id, raw_text)
                sys.stdout.write(json.dumps(enriched) + "\n")
                sys.stdout.flush()
            # A single failed generation must not abort the remaining records.
            except RuntimeError as e:
                logging.error("Failed processing video %s: %s", video_id, e)

# =====================================================================
# 5. RUNTIME ENTRYPOINT
# =====================================================================
def main(argv=None):
    """Parse args, select an enrichment strategy, and run the stdin stream."""
    logging.info("Pipeline Step 2B (LLM Enrichment) started.")

    parser = argparse.ArgumentParser(description="Multi-Provider Transcript Enrichment Node.")
    parser.add_argument(
        "--model",
        choices=["gemini", "claude"],
        default="gemini",
        help="Target LLM enrichment provider strategy (defaults to gemini).",
    )
    args = parser.parse_args(argv)

    try:
        if args.model == "claude":
            selected_strategy = ClaudeEnricher()
        else:
            selected_strategy = GeminiEnricher()
    # Provider setup failure is fatal --- there is nothing to stream without a client.
    except RuntimeError as e:
        logging.critical("Enrichment strategy initialization failed: %s", e)
        sys.exit(1)

    engine = EnrichmentEngine(selected_strategy)
    engine.run_stream()

    logging.info("Pipeline Step 2B finished.")


if __name__ == '__main__':
    main()
