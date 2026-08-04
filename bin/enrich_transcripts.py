#!/usr/bin/env python3
"""CLI entry point for transcript enrichment via a pluggable LLM provider."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.enrichment import main  # pylint: disable=wrong-import-position

if __name__ == "__main__":
    main()
