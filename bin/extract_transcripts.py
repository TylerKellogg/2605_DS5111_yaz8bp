

#!/usr/bin/env python3
"""Fetch YouTube transcripts for IDs read from stdin and emit them as JSON Lines.

Routes requests through a Webshare residential proxy when credentials are present
in the environment; falls back to direct IP routing otherwise.
"""

import sys
import os
import json
import logging
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

load_dotenv()

logging.basicConfig(
    filename='pipeline/logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Read video IDs from stdin, fetch transcripts, and emit JSONL to stdout."""
    logging.info("Pipeline Step 2A (Raw Extraction) started.")

    proxy_user = os.getenv("WEBSHARE_USER")
    proxy_pass = os.getenv("WEBSHARE_PASSWORD")

    if proxy_user and proxy_pass:
        logging.info(
            "Proxy credentials detected. Routing traffic via Webshare Residential network."
        )
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_user,
                proxy_password=proxy_pass,
            )
        )

    else:
        logging.warning("No proxy credentials found. Running with direct raw local IP routing.")
        ytt_api = YouTubeTranscriptApi()

    for line in sys.stdin:
        video_id = line.strip()
        if not video_id:
            continue

        logging.info("Processing transcript extraction for video: %s", video_id)

        try:
            # Execute the modern 2026 instance lookup method
            fetched_transcript = ytt_api.fetch(video_id)
            transcript_list = fetched_transcript.to_raw_data()

            # Stitch chunks with timestamp codes preserved for the staging file
            raw_text = " ".join([f"[{item['start']}] {item['text']}" for item in transcript_list])

            # Pack into a simple intermediary JSON object and emit to stdout
            payload = {"video_id": video_id, "raw_text": raw_text}
            sys.stdout.write(json.dumps(payload) + "\n")
            sys.stdout.flush()




        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Failed to fetch YouTube transcript for %s: %s", video_id, e)
            continue

    logging.info("Pipeline Step 2A finished.")

if __name__ == '__main__':
    main()
