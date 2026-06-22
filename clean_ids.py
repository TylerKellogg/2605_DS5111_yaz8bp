#!/usr/bin/env python3
# clean_ids.py
# Ready youtube IDs from stdin, print the valid ones, log the bad one
# valid ID is exactly 11 characters from A-Z, a-z, 0-9, - and _.

import sys
import re
import logging

logging.basicConfig(filename="pipeline_autid.log", level=logging.INFO)

pattern = re.compile("^[A-Za-z0-9_-]{11}$")

try:
    for line in sys.stdin:
        candidate = line.strip()
        if pattern.match(candidate):
            print(candidate)
        else:
            logging.info(f"invalid id: {candidate}")
except KeyboardInterrupt:
    pass
