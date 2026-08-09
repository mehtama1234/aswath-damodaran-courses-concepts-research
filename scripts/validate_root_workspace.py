#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import validate_applied_analysis
import validate_applied_evidence


def validate(workspace_root: Path) -> dict[str, dict[str, int]]:
    return {
        "applied_analysis": validate_applied_analysis.validate(workspace_root),
        "applied_evidence": validate_applied_evidence.validate(workspace_root),
    }


def format_summary(counts: dict[str, dict[str, int]]) -> str:
    analysis_counts = counts["applied_analysis"]
    evidence_counts = counts["applied_evidence"]
    return (
        "Root workspace validation passed: "
        f"applied-analysis={analysis_counts['analyses']} analyses/"
        f"{analysis_counts['root_concepts']} concepts/"
        f"{analysis_counts['root_theme_clusters']} theme clusters/"
        f"{analysis_counts['root_pages']} root pages; "
        f"applied-evidence={evidence_counts['briefs']} briefs/"
        f"{evidence_counts['theme_clusters']} theme clusters/"
        f"{evidence_counts['anchors']} anchors/"
        f"{evidence_counts['source_trails']} source trails"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run root workspace integrity validators for downstream applied layers."
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    args = parser.parse_args()
    workspace_root = args.workspace_root.resolve()

    counts = validate(workspace_root)
    print(format_summary(counts))


if __name__ == "__main__":
    main()
