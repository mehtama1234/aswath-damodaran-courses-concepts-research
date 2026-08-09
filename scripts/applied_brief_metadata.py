from __future__ import annotations

import json
import re
from pathlib import Path


def parse_front_matter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        return {}
    marker = "\n---\n"
    end = text.find(marker, 4)
    if end == -1:
        return {}

    metadata: dict[str, object] = {}
    current_key: str | None = None
    current_list: list[str] | None = None

    for raw_line in text[4:end].splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_key is not None and current_list is not None:
            current_list.append(line[4:].strip())
            continue
        if ": " in line:
            key, value = line.split(": ", 1)
            metadata[key.strip()] = value.strip()
            current_key = None
            current_list = None
            continue
        if line.endswith(":"):
            key = line[:-1].strip()
            current_list = []
            metadata[key] = current_list
            current_key = key
            continue

    return metadata


def strip_front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    marker = "\n---\n"
    end = text.find(marker, 4)
    if end == -1:
        return text
    return text[end + len(marker):]


def load_brief_metadata(path: Path) -> dict[str, object]:
    return parse_front_matter(path.read_text(encoding="utf-8"))


def resolve_metadata_ids(
    brief_id: str,
    field_name: str,
    requested_ids: list[str],
    existing_entries: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_id = {str(entry["id"]): entry for entry in existing_entries}
    missing = [entry_id for entry_id in requested_ids if entry_id not in by_id]
    if missing:
        raise ValueError(
            f"{brief_id}: {field_name} references unknown ids: {', '.join(missing)}"
        )
    return [by_id[entry_id] for entry_id in requested_ids]


def merge_catalog_item_with_brief_metadata(workspace_root: Path, item: dict[str, object]) -> dict[str, object]:
    merged = dict(item)
    metadata = load_brief_metadata(workspace_root / str(item["analysis_source"]))
    brief_id = str(metadata.get("brief_id") or item.get("id") or item["analysis_source"])

    for key in ("brief_id", "type", "title"):
        if key in metadata:
            merged[key] = metadata[key]

    if "root_concepts" in metadata and "root_concepts" in item:
        merged["root_concepts"] = resolve_metadata_ids(
            brief_id,
            "root_concepts",
            list(metadata["root_concepts"]),  # type: ignore[arg-type]
            list(item["root_concepts"]),  # type: ignore[arg-type]
        )

    if "root_theme_clusters" in metadata and "root_theme_clusters" in item:
        merged["root_theme_clusters"] = resolve_metadata_ids(
            brief_id,
            "root_theme_clusters",
            list(metadata["root_theme_clusters"]),  # type: ignore[arg-type]
            list(item["root_theme_clusters"]),  # type: ignore[arg-type]
        )

    if "brief_id" in merged and "id" not in merged:
        merged["id"] = merged["brief_id"]

    return merged


def load_merged_catalog_by_brief_id(workspace_root: Path) -> dict[str, dict[str, object]]:
    catalog = json.loads((workspace_root / "analysis/applied-analysis-catalog.json").read_text(encoding="utf-8"))
    merged_items = [
        merge_catalog_item_with_brief_metadata(workspace_root, item)
        for item in catalog["analyses"]
    ]
    return {str(item["id"]): item for item in merged_items}


def validate_evidence_registry_entry(
    catalog_entry: dict[str, object],
    registry_entry: dict[str, object],
) -> None:
    brief_id = str(registry_entry["brief_id"])

    expected_title = str(catalog_entry["title"])
    if str(registry_entry["brief_title"]) != expected_title:
        raise ValueError(
            f"{brief_id}: evidence registry brief_title does not match catalog title"
        )

    expected_href = str(catalog_entry["site_output"])
    if str(registry_entry["brief_href"]) != expected_href:
        raise ValueError(
            f"{brief_id}: evidence registry brief_href does not match catalog site_output"
        )

    expected_clusters = [str(entry["id"]) for entry in catalog_entry.get("root_theme_clusters", [])]
    actual_clusters = [str(entry["id"]) for entry in registry_entry.get("theme_cluster_refs", [])]
    if actual_clusters != expected_clusters:
        raise ValueError(
            f"{brief_id}: evidence registry theme_cluster_refs do not match catalog/root brief metadata"
        )


def validate_site_href_target(workspace_root: Path, href: str, *, context: str) -> None:
    if not href.startswith("site/"):
        raise ValueError(f"{context}: href must start with site/: {href}")

    path_part, _, fragment = href.partition("#")
    target_path = workspace_root / path_part
    if not target_path.exists():
        raise ValueError(f"{context}: target page does not exist: {href}")

    if not fragment:
        return

    html_text = target_path.read_text(encoding="utf-8")
    pattern = re.compile(r'id="' + re.escape(fragment) + r'"')
    if not pattern.search(html_text):
        raise ValueError(f"{context}: target fragment not found: {href}")


def known_source_trail_targets(workspace_root: Path) -> dict[str, Path]:
    return {
        "cross-course-comparison": workspace_root / "site/cross-course-comparison.html",
        "root-synthesis-essay": workspace_root / "site/root-synthesis-essay.html",
        "valuation-audience-comparison": workspace_root / "site/valuation-audience-comparison.html",
        "normalized-concepts-resolved": workspace_root / "analysis/normalized-concepts-resolved.json",
    }


def load_source_trail_registry(workspace_root: Path) -> dict[str, list[str]]:
    registry = json.loads((workspace_root / "analysis/source-trail-registry.json").read_text(encoding="utf-8"))
    return {
        str(prefix): [str(item) for item in items]
        for prefix, items in registry["allowed_tails_by_prefix"].items()
    }


def load_root_theme_cluster_names(workspace_root: Path) -> dict[str, str]:
    registry = json.loads((workspace_root / "analysis/root-themes-registry.json").read_text(encoding="utf-8"))
    return {
        str(cluster["id"]): str(cluster["name"])
        for cluster in registry["clusters"]
    }


def canonical_anchor_labels(workspace_root: Path) -> dict[str, str]:
    labels: dict[str, str] = {
        "site/cross-course-comparison.html": "Cross-Course Comparison",
        "site/valuation-audience-comparison.html": "Valuation Audience Comparison",
    }
    concepts_dir = workspace_root / "site/concepts"
    for path in concepts_dir.glob("*.html"):
        if path.name == "index.html":
            continue
        labels[f"site/concepts/{path.name}"] = path.stem.replace("-", " ").title()
    return labels


def validate_source_trail_entry(workspace_root: Path, entry: str, *, context: str) -> None:
    left, sep, right = entry.partition("::")
    if not sep:
        raise ValueError(f"{context}: source trail entry must contain '::': {entry}")

    left = left.strip()
    right = right.strip()
    if not left or not right:
        raise ValueError(f"{context}: source trail entry has empty side: {entry}")

    root_targets = known_source_trail_targets(workspace_root)
    allowed_tails = load_source_trail_registry(workspace_root)
    course_root = workspace_root / left
    if left in root_targets:
        if not root_targets[left].exists():
            raise ValueError(f"{context}: source trail target missing for {left}")
    elif not course_root.is_dir():
        raise ValueError(f"{context}: unknown source trail prefix: {left}")

    if left not in allowed_tails:
        raise ValueError(f"{context}: source trail prefix missing from registry: {left}")
    if right not in allowed_tails[left]:
        raise ValueError(f"{context}: source trail tail not allowed for {left}: {right}")

    file_match = re.match(r"([A-Za-z0-9_./-]+\.(?:json|md|html))(?::.*)?$", right)
    if file_match:
        relative_path = file_match.group(1)
        target_path = (workspace_root / left / relative_path) if course_root.is_dir() else (workspace_root / relative_path)
        if not target_path.exists():
            raise ValueError(f"{context}: source trail file does not exist: {entry}")


def validate_theme_cluster_ref_title(workspace_root: Path, cluster_ref: dict[str, object], *, context: str) -> None:
    cluster_names = load_root_theme_cluster_names(workspace_root)
    cluster_id = str(cluster_ref["id"])
    if cluster_id not in cluster_names:
        raise ValueError(f"{context}: unknown root theme cluster id: {cluster_id}")
    expected_title = cluster_names[cluster_id]
    actual_title = str(cluster_ref["title"])
    if actual_title != expected_title:
        raise ValueError(
            f"{context}: theme cluster title does not match registry name for {cluster_id}"
        )


def validate_anchor_label(workspace_root: Path, anchor: dict[str, object], *, context: str) -> None:
    href = str(anchor["root_href"])
    expected = canonical_anchor_labels(workspace_root).get(href)
    if expected is None:
        raise ValueError(f"{context}: no canonical anchor label registered for href: {href}")
    actual = str(anchor["label"])
    if actual != expected:
        raise ValueError(f"{context}: anchor label does not match canonical label for {href}")
