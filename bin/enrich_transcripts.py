#!/usr/bin/env python3
"""Enrich raw YouTube transcripts from stdin using the Gemini API.

Reads JSON Lines records, sends each transcript to Gemini under a strict
response schema, and emits schema-compliant enriched records to stdout.
"""
import sys
import os
import json
import logging
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from google import genai
from google.genai import types

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

def main():
    """Read transcript records from stdin, enrich via Gemini, emit JSONL to stdout."""
    logging.info("Pipeline Step 2B (Gemini Enrichment) started.")


    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical("GEMINI_API_KEY not found in environment. Terminating pipeline.")
        sys.exit(1)
    client = genai.Client(api_key=api_key)


    response_schema = {
        "type": "OBJECT",
        "properties": {
            "video_id": {"type": "STRING"},
            "cleaned_text": {"type": "STRING"},
            "tech_terms": {"type": "ARRAY", "items": {"type": "STRING"}},
            "book_names": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["video_id", "cleaned_text"],
    }


    # Stream processing framework reading line-by-line text inputs from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue


        try:
            payload = json.loads(line)
            video_id = payload["video_id"]
            raw_text = payload["raw_text"]
        # One corrupt row must not kill the stream ---- log  and continue.
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Failed to parse incoming JSON payload row: %s", e)
            continue

        logging.info("Orchestrating Gemini enrichment for video: %s", video_id)

        prompt = f"""
        You are an elite data engineer. Clean this transcript text for video_id '{video_id}'.
        1. Strip all timestamps and duration codes.
        2. Extract technical architecture terms and books.
        """

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{prompt}\n\nTRANSCRIPT:\n{raw_text}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )
            enriched = json.loads(response.text)
            sys.stdout.write(json.dumps(enriched) + "\n")
            sys.stdout.flush()
        # A single failed generation must not abort the remaining records.
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Failed processing video %s during LLM generation: %s", video_id, e)

    logging.info("Pipeline Step 2B finished.")

if __name__ == '__main__':
    main()
