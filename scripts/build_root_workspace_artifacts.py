#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import build_resolved_normalized_concepts
import build_cross_course_comparison_page
import build_valuation_audience_comparison_page
import build_root_synthesis_page
import build_root_themes_atlas_page
import build_root_themes_registry_page
import build_sector_company_framework_page
import build_root_applied_analysis_pages
import build_applied_analysis_index_page
import build_applied_evidence_page
import build_root_concept_atlas
import build_root_evidence_index
import build_root_file_evidence_index
import validate_root_workspace


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild the root Damodaran workspace analysis and concept-atlas artifacts."
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the aswath-damodaran-courses-concepts-research workspace root.",
    )
    args = parser.parse_args()
    workspace_root = args.workspace_root.resolve()

    print(f"[1/13] Building root session evidence index for {workspace_root}")
    build_root_evidence_index.write_json(
        workspace_root / "analysis/course-evidence-index.json",
        build_root_evidence_index.build(workspace_root),
    )

    print("[2/13] Building root file evidence index")
    build_root_file_evidence_index.write_json(
        workspace_root / "analysis/course-file-evidence-index.json",
        build_root_file_evidence_index.build(workspace_root),
    )

    print("[3/13] Resolving normalized concepts to canonical evidence ids")
    build_resolved_normalized_concepts.write_json(
        workspace_root / "analysis/normalized-concepts-resolved.json",
        build_resolved_normalized_concepts.build(workspace_root),
    )

    print("[4/13] Rebuilding normalized concepts overview and concept atlas pages")
    build_root_concept_atlas.build(workspace_root)

    print("[5/13] Rebuilding cross-course comparison page")
    build_cross_course_comparison_page.build(workspace_root)

    print("[6/13] Rebuilding valuation audience comparison page")
    build_valuation_audience_comparison_page.build(workspace_root)

    print("[7/13] Rebuilding root synthesis essay page")
    build_root_synthesis_page.build(workspace_root)

    print("[8/13] Rebuilding root themes atlas page")
    build_root_themes_atlas_page.build(workspace_root)

    print("[9/13] Rebuilding root themes registry page")
    build_root_themes_registry_page.build(workspace_root)

    print("[10/13] Rebuilding sector and company writeup framework page")
    build_sector_company_framework_page.build(workspace_root)

    print("[11/13] Rebuilding root applied analysis pages")
    build_root_applied_analysis_pages.build(workspace_root)

    print("[12/13] Rebuilding applied analysis index page")
    build_applied_analysis_index_page.build(workspace_root)

    print("[13/13] Rebuilding applied evidence page")
    build_applied_evidence_page.build(workspace_root)

    print("[post] Running root workspace validators")
    validation_counts = validate_root_workspace.validate(workspace_root)
    print(validate_root_workspace.format_summary(validation_counts))

    print("Root workspace artifacts rebuilt successfully.")


if __name__ == "__main__":
    main()
