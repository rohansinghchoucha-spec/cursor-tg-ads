#!/usr/bin/env python3
"""Render tg_audit.py JSON lines as a sorted table (highest live views first)."""

import json
import sys

rows = []
for line in sys.stdin:
    line = line.strip()
    if line:
        rows.append(json.loads(line))

rows.sort(key=lambda d: -(d.get("views_med") or 0))
for d in rows:
    print("{:33} {:9} med={:6} max={:6} last={:10} {}".format(
        d.get("handle", "")[:33],
        (d.get("state") or "")[:9],
        d.get("views_med") or 0,
        d.get("views_max") or 0,
        str(d.get("last_post") or "-")[:10],
        (d.get("title") or "")[:40],
    ))
