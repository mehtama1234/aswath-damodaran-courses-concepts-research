#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from applied_brief_metadata import (
    canonical_anchor_labels,
    load_brief_metadata,
    load_root_theme_cluster_names,
    merge_catalog_item_with_brief_metadata,
    validate_site_href_target,
)


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(workspace_root: Path) -> dict[str, int]:
    catalog = load_catalog(workspace_root / "analysis/applied-analysis-catalog.json")
    evidence_registry = load_catalog(workspace_root / "analysis/applied-evidence-registry.json")
    evidence_by_brief_id = {str(item["brief_id"]): item for item in evidence_registry["briefs"]}
    root_theme_names = load_root_theme_cluster_names(workspace_root)
    canonical_concept_labels = canonical_anchor_labels(workspace_root)

    counts = {
        "analyses": 0,
        "root_concepts": 0,
        "root_theme_clusters": 0,
        "root_pages": 0,
    }

    seen_ids: set[str] = set()
    seen_site_outputs: set[str] = set()

    for raw_item in catalog["analyses"]:
        item = merge_catalog_item_with_brief_metadata(workspace_root, raw_item)
        brief_id = str(item["id"])

        if brief_id in seen_ids:
            raise ValueError(f"{brief_id}: duplicate applied-analysis id")
        seen_ids.add(brief_id)

        metadata = load_brief_metadata(workspace_root / str(item["analysis_source"]))
        if str(metadata.get("brief_id")) != brief_id:
            raise ValueError(f"{brief_id}: brief front matter brief_id mismatch")
        if str(metadata.get("title")) != str(item["title"]):
            raise ValueError(f"{brief_id}: brief front matter title mismatch")
        if str(metadata.get("type")) != str(item["type"]):
            raise ValueError(f"{brief_id}: brief front matter type mismatch")

        analysis_source = workspace_root / str(item["analysis_source"])
        if not analysis_source.exists():
            raise ValueError(f"{brief_id}: analysis source missing: {item['analysis_source']}")
        if analysis_source.stem != brief_id:
            raise ValueError(f"{brief_id}: analysis source filename does not match brief id")

        site_output = str(item["site_output"])
        if site_output in seen_site_outputs:
            raise ValueError(f"{brief_id}: duplicate site_output {site_output}")
        seen_site_outputs.add(site_output)
        validate_site_href_target(workspace_root, site_output, context=f"{brief_id}: site_output")
        if Path(site_output).stem != brief_id:
            raise ValueError(f"{brief_id}: site_output filename does not match brief id")

        evidence_ref = item["evidence_registry_ref"]
        if str(evidence_ref["brief_id"]) != brief_id:
            raise ValueError(f"{brief_id}: evidence_registry_ref brief_id mismatch")
        if str(evidence_ref["registry_path"]) != "analysis/applied-evidence-registry.json":
            raise ValueError(f"{brief_id}: unexpected evidence_registry_ref registry_path")
        if str(evidence_ref["site_page"]) != "site/applied-evidence.html":
            raise ValueError(f"{brief_id}: unexpected evidence_registry_ref site_page")
        registry_path = workspace_root / str(evidence_ref["registry_path"])
        if not registry_path.exists():
            raise ValueError(f"{brief_id}: evidence_registry_ref registry_path missing")
        if brief_id not in evidence_by_brief_id:
            raise ValueError(f"{brief_id}: missing evidence-registry entry")
        if str(evidence_by_brief_id[brief_id]["brief_title"]) != str(item["title"]):
            raise ValueError(f"{brief_id}: evidence-registry brief_title mismatch")
        if str(evidence_by_brief_id[brief_id]["brief_href"]) != site_output:
            raise ValueError(f"{brief_id}: evidence-registry brief_href mismatch")
        validate_site_href_target(
            workspace_root,
            str(evidence_ref["site_page"]),
            context=f"{brief_id}: evidence_registry_ref.site_page",
        )

        for concept in item["root_concepts"]:
            concept_href = str(concept["href"])
            validate_site_href_target(
                workspace_root,
                concept_href,
                context=f"{brief_id}: root_concepts[{concept['id']}]",
            )
            expected_title = canonical_concept_labels.get(concept_href)
            if expected_title is None:
                raise ValueError(f"{brief_id}: no canonical concept label for {concept_href}")
            if str(concept["title"]) != expected_title:
                raise ValueError(f"{brief_id}: root concept title mismatch for {concept_href}")
            counts["root_concepts"] += 1

        for cluster in item.get("root_theme_clusters", []):
            cluster_id = str(cluster["id"])
            if cluster_id not in root_theme_names:
                raise ValueError(f"{brief_id}: unknown root theme cluster id {cluster_id}")
            if str(cluster["title"]) != root_theme_names[cluster_id]:
                raise ValueError(f"{brief_id}: root theme cluster title mismatch for {cluster_id}")
            validate_site_href_target(
                workspace_root,
                str(cluster["href"]),
                context=f"{brief_id}: root_theme_clusters[{cluster_id}]",
            )
            counts["root_theme_clusters"] += 1

        for root_page in item["root_pages"]:
            validate_site_href_target(
                workspace_root,
                str(root_page),
                context=f"{brief_id}: root_pages",
            )
            counts["root_pages"] += 1

        counts["analyses"] += 1

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate applied analysis catalog integrity.")
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
        "Applied analysis validation passed:",
        f"{counts['analyses']} analyses,",
        f"{counts['root_concepts']} root concepts,",
        f"{counts['root_theme_clusters']} root theme clusters,",
        f"{counts['root_pages']} root pages",
    )


if __name__ == "__main__":
    main()
