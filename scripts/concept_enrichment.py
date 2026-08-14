"""Shared loader/renderer for per-course concept enrichment.

Each course keeps an optional ``analysis/concept-enrichment.json`` sidecar keyed by
concept slug. Each value may supply a numeric ``worked_example`` and a
``failure_boundary`` (where the approach stops being trustworthy). Concept prose in
the builders stays untouched; these sidecars only add the two sections the concept
pages were missing. Everything is backward-compatible: no sidecar, or a slug with no
entry, renders nothing.
"""
from __future__ import annotations

import json
import os
from typing import Any

_CACHE: dict[str, dict[str, Any]] = {}


def load_enrichment(course_root: Any) -> dict[str, Any]:
    path = os.path.join(str(course_root), "analysis", "concept-enrichment.json")
    if path not in _CACHE:
        try:
            with open(path, encoding="utf-8") as fh:
                loaded = json.load(fh)
            _CACHE[path] = loaded if isinstance(loaded, dict) else {}
        except (OSError, ValueError):
            _CACHE[path] = {}
    return _CACHE[path]


def enrichment_html(esc, entry: Any) -> str:
    """Render the worked-example and failure-boundary sections for one concept."""
    if not isinstance(entry, dict):
        return ""
    parts: list[str] = []
    worked = entry.get("worked_example")
    failure = entry.get("failure_boundary")
    if worked and str(worked).strip():
        paras = "".join(f"<p>{esc(p)}</p>" for p in str(worked).split("\n\n") if p.strip())
        parts.append(f"<h3>Worked example</h3>{paras}")
    if failure and str(failure).strip():
        paras = "".join(f"<p>{esc(p)}</p>" for p in str(failure).split("\n\n") if p.strip())
        parts.append(f"<h3>Where the approach breaks</h3>{paras}")
    return "".join(parts)
