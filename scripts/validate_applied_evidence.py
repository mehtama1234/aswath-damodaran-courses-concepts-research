#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from applied_brief_metadata import (
    load_merged_catalog_by_brief_id,
    validate_anchor_label,
    validate_evidence_registry_entry,
    validate_site_href_target,
    validate_source_trail_entry,
    validate_theme_cluster_ref_title,
)


def load_registry(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(workspace_root: Path) -> dict[str, int]:
    registry = load_registry(workspace_root / "analysis/applied-evidence-registry.json")
    catalog_by_brief_id = load_merged_catalog_by_brief_id(workspace_root)

    counts = {
        "briefs": 0,
        "theme_clusters": 0,
        "anchors": 0,
        "source_trails": 0,
    }

    for brief in registry["briefs"]:
        brief_id = str(brief["brief_id"])
        if brief_id not in catalog_by_brief_id:
            raise ValueError(f"{brief_id}: evidence registry references unknown applied brief id")
        validate_evidence_registry_entry(catalog_by_brief_id[brief_id], brief)
        counts["briefs"] += 1

        for cluster in brief.get("theme_cluster_refs", []):
            validate_theme_cluster_ref_title(
                workspace_root,
                cluster,
                context=f'{brief_id}: theme_cluster_refs[{cluster["id"]}]',
            )
            validate_site_href_target(
                workspace_root,
                str(cluster["root_href"]),
                context=f'{brief_id}: theme_cluster_refs[{cluster["id"]}]',
            )
            counts["theme_clusters"] += 1

        for anchor in brief["anchors"]:
            validate_anchor_label(
                workspace_root,
                anchor,
                context=f'{brief_id}: anchors[{anchor["label"]}]',
            )
            validate_site_href_target(
                workspace_root,
                str(anchor["root_href"]),
                context=f'{brief_id}: anchors[{anchor["label"]}]',
            )
            counts["anchors"] += 1
            for trail_item in anchor["source_trail"]:
                validate_source_trail_entry(
                    workspace_root,
                    str(trail_item),
                    context=f'{brief_id}: anchors[{anchor["label"]}]',
                )
                counts["source_trails"] += 1

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate applied evidence registry integrity.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    args = parser.parse_args()
    workspace_root = args.workspace_root.resolve()

    counts = validate(workspace_root)
    print(
        "Applied evidence validation passed:",
        f"{counts['briefs']} briefs,",
        f"{counts['theme_clusters']} theme clusters,",
        f"{counts['anchors']} anchors,",
        f"{counts['source_trails']} source trails",
    )


if __name__ == "__main__":
    main()
