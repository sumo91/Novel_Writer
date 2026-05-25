import argparse
from pathlib import Path

from engine.acceptance_packet import draft_acceptance_packet
from engine.brief_contract import (
    build_chapter_brief_scaffold,
    check_chapter_brief,
    default_brief_path,
)
from engine.book_factory import create_book
from engine.context_builder import write_context
from engine.craft_contract import (
    check_craft_contract,
    generate_concept_review,
    write_craft_contract_scaffold,
)
from engine.drift_report import generate_drift_report
from engine.html_utils import write_markdown_html_sidecar
from engine.outline_approval_packet import (
    SUPPORTED_LAYERS as OUTLINE_APPROVAL_PACKET_LAYERS,
    generate_outline_approval_packet,
)
from engine.outline_map_review import generate_outline_map_review
from engine.pending_approvals import (
    PendingApprovalNotFoundError,
    batch_update_pending_approvals,
    render_pending_approvals,
    sync_pending_approvals,
    update_pending_approval,
)
from engine.reader_panel import write_reader_panel_review_scaffold
from engine.style_knowledge import (
    check_style_calibration,
    check_style_bible,
    load_style_profiles,
    write_style_calibration_scaffold,
    write_style_bible_from_profile,
    write_style_bible_scaffold,
)
from engine.io_utils import read_yaml
from engine.outline_gate import (
    APPROVAL_STATUSES,
    OUTLINE_LAYERS,
    chapter_brief_gate,
    get_outline_status,
    update_outline_approval,
)
from engine.pipeline import (
    pipeline_accept_update_file,
    pipeline_accept,
    pipeline_draft_acceptance,
    pipeline_quality_gate,
    pipeline_prose_quality_gate,
    pipeline_status,
    prepare_chapter,
    write_author_direction_scaffold,
    write_quality_gate_html,
)
from engine.v3_migration import migrate_book_to_v3, migrate_book_to_v3_1
from engine.validators import validate_book


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="novel-writer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_book = subparsers.add_parser("init-book", help="Create a new book project.")
    init_book.add_argument("book_id")
    init_book.add_argument("--title", required=True)
    init_book.add_argument("--force", action="store_true")

    validate_book_cmd = subparsers.add_parser(
        "validate-book", help="Validate a book project structure."
    )
    validate_book_cmd.add_argument("book_id")

    build_context = subparsers.add_parser(
        "build-context", help="Build a Markdown context pack for a chapter."
    )
    build_context.add_argument("book_id")
    build_context.add_argument("chapter_number", type=int)
    build_context.add_argument("--output", required=True)

    accept_chapter_cmd = subparsers.add_parser(
        "accept-chapter",
        help="Apply an approved chapter acceptance update packet.",
    )
    accept_chapter_cmd.add_argument("book_id")
    accept_chapter_cmd.add_argument("--update-file", required=True)
    accept_chapter_cmd.add_argument("--approved", action="store_true")
    accept_chapter_cmd.add_argument("--force", action="store_true")

    draft_packet_cmd = subparsers.add_parser(
        "draft-acceptance-packet",
        help="Draft a chapter acceptance packet for human review.",
    )
    draft_packet_cmd.add_argument("book_id")
    draft_packet_cmd.add_argument("chapter_number", type=int)
    draft_packet_cmd.add_argument("--title", required=True)
    draft_packet_cmd.add_argument("--source-draft", required=True)
    draft_packet_cmd.add_argument("--summary", required=True)
    draft_packet_cmd.add_argument("--output")
    draft_packet_cmd.add_argument("--force", action="store_true")

    prepare_chapter_cmd = subparsers.add_parser(
        "prepare-chapter",
        help="Prepare a V2 chapter pipeline workspace.",
    )
    prepare_chapter_cmd.add_argument("book_id")
    prepare_chapter_cmd.add_argument("chapter_number", type=int)
    prepare_chapter_cmd.add_argument("--force", action="store_true")

    pipeline_status_cmd = subparsers.add_parser(
        "pipeline-status",
        help="Report V2 chapter pipeline artifact status.",
    )
    pipeline_status_cmd.add_argument("book_id")
    pipeline_status_cmd.add_argument("chapter_number", type=int)

    pipeline_quality_cmd = subparsers.add_parser(
        "pipeline-quality-gate",
        help="Evaluate the V2.5 chapter quality gate.",
    )
    pipeline_quality_cmd.add_argument("book_id")
    pipeline_quality_cmd.add_argument("chapter_number", type=int)

    prose_quality_cmd = subparsers.add_parser(
        "pipeline-prose-quality-gate",
        help="Evaluate the V4.1 prose quality gate.",
    )
    prose_quality_cmd.add_argument("book_id")
    prose_quality_cmd.add_argument("chapter_number", type=int)

    author_direction_cmd = subparsers.add_parser(
        "author-direction-scaffold",
        help="Write a lightweight human author direction scaffold.",
    )
    author_direction_cmd.add_argument("book_id")
    author_direction_cmd.add_argument("chapter_number", type=int)
    author_direction_cmd.add_argument("--force", action="store_true")

    reader_panel_cmd = subparsers.add_parser(
        "reader-panel-review",
        help="Write a non-canon simulated reader panel review scaffold.",
    )
    reader_panel_cmd.add_argument("book_id")
    reader_panel_cmd.add_argument("chapter_number", type=int)
    reader_panel_cmd.add_argument("--force", action="store_true")

    style_bible_scaffold_cmd = subparsers.add_parser(
        "style-bible-scaffold",
        help="Write a book-local Style Bible scaffold.",
    )
    style_bible_scaffold_cmd.add_argument("book_id")
    style_bible_scaffold_cmd.add_argument("--force", action="store_true")

    style_bible_check_cmd = subparsers.add_parser(
        "style-bible-check",
        help="Check a book-local Style Bible contract.",
    )
    style_bible_check_cmd.add_argument("book_id")

    craft_contract_scaffold_cmd = subparsers.add_parser(
        "craft-contract-scaffold",
        help="Write a book-local craft contract scaffold.",
    )
    craft_contract_scaffold_cmd.add_argument("book_id")
    craft_contract_scaffold_cmd.add_argument("--force", action="store_true")

    craft_contract_check_cmd = subparsers.add_parser(
        "craft-contract-check",
        help="Check a book-local craft contract.",
    )
    craft_contract_check_cmd.add_argument("book_id")

    concept_review_cmd = subparsers.add_parser(
        "concept-review",
        help="Generate a craft-card-driven concept review scaffold.",
    )
    concept_review_cmd.add_argument("book_id")
    concept_review_cmd.add_argument("--output")

    style_calibration_scaffold_cmd = subparsers.add_parser(
        "style-calibration-scaffold",
        help="Write a book-local style calibration scaffold.",
    )
    style_calibration_scaffold_cmd.add_argument("book_id")
    style_calibration_scaffold_cmd.add_argument("--force", action="store_true")

    style_calibration_check_cmd = subparsers.add_parser(
        "style-calibration-check",
        help="Check a book-local style calibration contract.",
    )
    style_calibration_check_cmd.add_argument("book_id")

    subparsers.add_parser(
        "style-profile-list",
        help="List reusable abstract style profiles.",
    )

    style_bible_from_profile_cmd = subparsers.add_parser(
        "style-bible-from-profile",
        help="Write a book-local Style Bible from an abstract style profile.",
    )
    style_bible_from_profile_cmd.add_argument("book_id")
    style_bible_from_profile_cmd.add_argument("profile_id")
    style_bible_from_profile_cmd.add_argument("--force", action="store_true")

    pipeline_draft_cmd = subparsers.add_parser(
        "pipeline-draft-acceptance",
        help="Draft an acceptance packet from the V2 pipeline defaults.",
    )
    pipeline_draft_cmd.add_argument("book_id")
    pipeline_draft_cmd.add_argument("chapter_number", type=int)
    pipeline_draft_cmd.add_argument("--title", required=True)
    pipeline_draft_cmd.add_argument("--summary", required=True)
    pipeline_draft_cmd.add_argument("--force", action="store_true")
    pipeline_draft_cmd.add_argument("--allow-missing-reviews", action="store_true")

    pipeline_accept_cmd = subparsers.add_parser(
        "pipeline-accept",
        help="Apply a pipeline acceptance packet after explicit human approval.",
    )
    pipeline_accept_cmd.add_argument("book_id")
    pipeline_accept_cmd.add_argument("chapter_number", type=int)
    pipeline_accept_cmd.add_argument("--approved", action="store_true")
    pipeline_accept_cmd.add_argument("--force", action="store_true")

    drift_report_cmd = subparsers.add_parser(
        "drift-report",
        help="Generate a chapter-range drift review report.",
    )
    drift_report_cmd.add_argument("book_id")
    drift_report_cmd.add_argument("--start", type=int, required=True)
    drift_report_cmd.add_argument("--end", type=int, required=True)
    drift_report_cmd.add_argument("--output")

    pending_cmd = subparsers.add_parser(
        "pending-approvals",
        help="List deduped pending approvals with source chapters.",
    )
    pending_cmd.add_argument("book_id")

    sync_pending_cmd = subparsers.add_parser(
        "sync-pending-approvals",
        help="Write deduped pending approvals to state/pending_approvals.yaml.",
    )
    sync_pending_cmd.add_argument("book_id")

    update_pending_cmd = subparsers.add_parser(
        "pending-approval-update",
        help="Update one pending approval status in state/pending_approvals.yaml.",
    )
    update_pending_cmd.add_argument("book_id")
    update_pending_cmd.add_argument("approval_id")
    update_pending_cmd.add_argument(
        "--status",
        required=True,
        choices=["open", "approved", "rejected", "deferred"],
    )
    update_pending_cmd.add_argument("--note")

    batch_update_pending_cmd = subparsers.add_parser(
        "pending-approval-batch-update",
        help="Update multiple pending approval statuses in one registry write.",
    )
    batch_update_pending_cmd.add_argument("book_id")
    batch_update_pending_cmd.add_argument("--updates-file", required=True)

    migrate_v3_cmd = subparsers.add_parser(
        "migrate-v3",
        help="Add missing lightweight V3 state files to an existing book project.",
    )
    migrate_v3_cmd.add_argument("book_id")

    migrate_v3_1_cmd = subparsers.add_parser(
        "migrate-v3-1",
        help="Add missing V3.1 long-form outline architecture files to a book project.",
    )
    migrate_v3_1_cmd.add_argument("book_id")

    outline_status_cmd = subparsers.add_parser(
        "outline-status",
        help="Report V3.1 outline approval status.",
    )
    outline_status_cmd.add_argument("book_id")

    outline_map_review_cmd = subparsers.add_parser(
        "outline-map-review",
        help="Generate a readable minimum-map review for V3.1 outlines.",
    )
    outline_map_review_cmd.add_argument("book_id")

    outline_approval_packet_cmd = subparsers.add_parser(
        "outline-approval-packet",
        help="Generate a human-readable outline approval packet.",
    )
    outline_approval_packet_cmd.add_argument("book_id")
    outline_approval_packet_cmd.add_argument(
        "--layer",
        required=True,
        choices=sorted(OUTLINE_APPROVAL_PACKET_LAYERS),
    )

    outline_approval_cmd = subparsers.add_parser(
        "outline-approval-update",
        help="Update one V3.1 outline layer approval status.",
    )
    outline_approval_cmd.add_argument("book_id")
    outline_approval_cmd.add_argument("layer", choices=sorted(OUTLINE_LAYERS))
    outline_approval_cmd.add_argument(
        "--status",
        required=True,
        choices=sorted(APPROVAL_STATUSES),
    )
    outline_approval_cmd.add_argument("--note")

    chapter_brief_gate_cmd = subparsers.add_parser(
        "chapter-brief-gate",
        help="Check whether a chapter brief can proceed under V3.1 outline gates.",
    )
    chapter_brief_gate_cmd.add_argument("book_id")
    chapter_brief_gate_cmd.add_argument("chapter_number", type=int)
    chapter_brief_gate_cmd.add_argument("--strict", action="store_true")

    chapter_brief_scaffold_cmd = subparsers.add_parser(
        "chapter-brief-scaffold",
        help="Write a V3.3 chapter brief scaffold.",
    )
    chapter_brief_scaffold_cmd.add_argument("book_id")
    chapter_brief_scaffold_cmd.add_argument("chapter_number", type=int)
    chapter_brief_scaffold_cmd.add_argument("--output")
    chapter_brief_scaffold_cmd.add_argument("--force", action="store_true")

    chapter_brief_check_cmd = subparsers.add_parser(
        "chapter-brief-check",
        help="Check an existing chapter brief against the V3.3 contract.",
    )
    chapter_brief_check_cmd.add_argument("book_id")
    chapter_brief_check_cmd.add_argument("chapter_number", type=int)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-book":
        created = create_book(args.book_id, args.title, force=args.force)
        print(f"Created book project: {Path(created).as_posix()}")
        return 0

    if args.command == "validate-book":
        errors = validate_book(args.book_id)
        if errors:
            for error in errors:
                print(error)
            return 1
        print(f"Book project is valid: {args.book_id}")
        return 0

    if args.command == "build-context":
        output_path = write_context(
            args.book_id,
            args.chapter_number,
            Path(args.output),
        )
        print(f"Wrote chapter context: {output_path.as_posix()}")
        return 0

    if args.command == "accept-chapter":
        try:
            chapter_path = pipeline_accept_update_file(
                args.book_id,
                Path(args.update_file),
                approved=args.approved,
                force=args.force,
            )
        except (PermissionError, FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Accepted chapter: {chapter_path.as_posix()}")
        return 0

    if args.command == "draft-acceptance-packet":
        output_path = draft_acceptance_packet(
            args.book_id,
            args.chapter_number,
            title=args.title,
            source_draft=args.source_draft,
            summary=args.summary,
            output_path=Path(args.output) if args.output else None,
            force=args.force,
        )
        print(f"Drafted acceptance packet: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "prepare-chapter":
        paths = prepare_chapter(args.book_id, args.chapter_number, force=args.force)
        print(f"Prepared chapter pipeline: {paths.pipeline_dir.as_posix()}")
        gate = chapter_brief_gate(args.book_id, args.chapter_number)
        gate_status = "allowed" if gate["allowed"] else "blocked"
        print(f"Chapter brief gate: {gate_status}")
        check = check_chapter_brief(args.book_id, args.chapter_number)
        print(f"Chapter brief check: {check['status']}")
        return 0

    if args.command == "pipeline-status":
        status = pipeline_status(args.book_id, args.chapter_number)
        print(f"Pipeline status: {status['status']}")
        for name, artifact in status["artifacts"].items():
            marker = "present" if artifact["present"] else "missing"
            print(f"- {name}: {marker} ({artifact['path']})")
        print(f"Next action: {status['next_action']}")
        return 0

    if args.command == "pipeline-quality-gate":
        try:
            result = pipeline_quality_gate(args.book_id, args.chapter_number)
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Quality gate: {result['status']}")
        print(f"- continuity_blockers: {len(result['continuity_blockers'])}")
        print(f"- initial_pacing_score: {result['initial_pacing_score']}")
        print(f"- revised_pacing_score: {result['revised_pacing_score']}")
        print(f"- revision_required: {result['revision_required']}")
        print(f"- waiver_required: {result['waiver_required']}")
        for reason in result["reasons"]:
            print(f"- reason: {reason}")
        html_path = write_quality_gate_html(args.book_id, args.chapter_number, result)
        print(f"HTML review copy: {html_path.as_posix()}")
        return 0 if result["passed"] else 1

    if args.command == "pipeline-prose-quality-gate":
        try:
            result = pipeline_prose_quality_gate(args.book_id, args.chapter_number)
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Prose quality gate: {result['status']}")
        print(f"- score: {result['score']}")
        print(f"- rewrite_required: {result['rewrite_required']}")
        for reason in result["reasons"]:
            print(f"- reason: {reason}")
        return 0 if result["passed"] else 1

    if args.command == "author-direction-scaffold":
        try:
            output_path = write_author_direction_scaffold(
                args.book_id,
                args.chapter_number,
                force=args.force,
            )
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Wrote author direction scaffold: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "reader-panel-review":
        try:
            output_path = write_reader_panel_review_scaffold(
                args.book_id,
                args.chapter_number,
                force=args.force,
            )
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Wrote reader panel review scaffold: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "style-bible-scaffold":
        try:
            output_path = write_style_bible_scaffold(args.book_id, force=args.force)
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Wrote style bible scaffold: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "style-bible-check":
        try:
            result = check_style_bible(args.book_id)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Style bible check: {result['status']}")
        for warning in result["warnings"]:
            print(f"- warning: {warning}")
        for error in result["errors"]:
            print(f"- error: {error}")
        return 0 if result["passed"] else 1

    if args.command == "craft-contract-scaffold":
        try:
            output_path = write_craft_contract_scaffold(args.book_id, force=args.force)
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Wrote craft contract scaffold: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "craft-contract-check":
        try:
            result = check_craft_contract(args.book_id)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Craft contract check: {result['status']}")
        for warning in result["warnings"]:
            print(f"- warning: {warning}")
        for error in result["errors"]:
            print(f"- error: {error}")
        return 0 if result["passed"] else 1

    if args.command == "concept-review":
        try:
            output_path = generate_concept_review(
                args.book_id,
                Path(args.output) if args.output else None,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Generated concept review: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "style-calibration-scaffold":
        try:
            output_path = write_style_calibration_scaffold(
                args.book_id,
                force=args.force,
            )
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Wrote style calibration scaffold: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "style-calibration-check":
        try:
            result = check_style_calibration(args.book_id)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Style calibration check: {result['status']}")
        for warning in result["warnings"]:
            print(f"- warning: {warning}")
        for error in result["errors"]:
            print(f"- error: {error}")
        return 0 if result["passed"] else 1

    if args.command == "style-profile-list":
        profiles = load_style_profiles()
        print("Style profiles:")
        for profile in profiles:
            print(
                f"- {profile['id']}: {profile.get('label', '')} "
                f"({profile.get('source', '')})"
            )
            if profile.get("use_when"):
                print(f"  Use when: {profile['use_when']}")
        return 0

    if args.command == "style-bible-from-profile":
        try:
            output_path = write_style_bible_from_profile(
                args.book_id,
                args.profile_id,
                force=args.force,
            )
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Wrote style bible from profile: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "pipeline-draft-acceptance":
        output_path = pipeline_draft_acceptance(
            args.book_id,
            args.chapter_number,
            title=args.title,
            summary=args.summary,
            force=args.force,
            allow_missing_reviews=args.allow_missing_reviews,
        )
        print(f"Drafted pipeline acceptance packet: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "pipeline-accept":
        chapter_path = pipeline_accept(
            args.book_id,
            args.chapter_number,
            approved=args.approved,
            force=args.force,
        )
        print(f"Pipeline accepted chapter: {chapter_path.as_posix()}")
        return 0

    if args.command == "drift-report":
        output_path = generate_drift_report(
            args.book_id,
            args.start,
            args.end,
            Path(args.output) if args.output else None,
        )
        print(f"Generated drift report: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "pending-approvals":
        print(render_pending_approvals(args.book_id), end="")
        return 0

    if args.command == "sync-pending-approvals":
        output_path = sync_pending_approvals(args.book_id)
        print(f"Synced pending approvals: {output_path.as_posix()}")
        return 0

    if args.command == "pending-approval-update":
        try:
            update_pending_approval(
                args.book_id,
                args.approval_id,
                status=args.status,
                note=args.note,
            )
        except (FileNotFoundError, ValueError, PendingApprovalNotFoundError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Updated pending approval: {args.approval_id} -> {args.status}")
        return 0

    if args.command == "pending-approval-batch-update":
        try:
            updates_doc = read_yaml(Path(args.updates_file))
            updates = updates_doc.get("updates")
            if not isinstance(updates, list):
                raise ValueError("Updates file must contain an updates list.")
            batch_update_pending_approvals(args.book_id, updates)
        except (FileNotFoundError, ValueError, PendingApprovalNotFoundError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Batch updated pending approvals: {len(updates)}")
        return 0

    if args.command == "migrate-v3":
        try:
            result = migrate_book_to_v3(args.book_id)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Migrated book to V3: {result.book_id}")
        for path in result.created:
            print(f"- created: {path}")
        for path in result.updated:
            print(f"- updated: {path}")
        return 0

    if args.command == "migrate-v3-1":
        try:
            result = migrate_book_to_v3_1(args.book_id)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Migrated book to V3.1: {result.book_id}")
        for path in result.created:
            print(f"- created: {path}")
        for path in result.updated:
            print(f"- updated: {path}")
        return 0

    if args.command == "outline-status":
        try:
            status = get_outline_status(args.book_id)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Outline status: {args.book_id}")
        for layer in status["layers"]:
            marker = layer["approval_status"]
            if not layer["exists"]:
                marker = "missing"
            print(f"- {layer['layer']}: {marker} ({layer['path']})")
        return 0

    if args.command == "outline-map-review":
        try:
            output_path = generate_outline_map_review(args.book_id)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Generated outline map review: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "outline-approval-packet":
        try:
            output_path = generate_outline_approval_packet(
                args.book_id,
                layer=args.layer,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Generated outline approval packet: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "outline-approval-update":
        try:
            update_outline_approval(
                args.book_id,
                args.layer,
                status=args.status,
                note=args.note,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Updated outline approval: {args.layer} -> {args.status}")
        return 0

    if args.command == "chapter-brief-gate":
        try:
            result = chapter_brief_gate(
                args.book_id,
                args.chapter_number,
                strict=args.strict,
            )
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        status = "allowed" if result["allowed"] else "blocked"
        print(f"Chapter brief gate: {status}")
        print(f"- brief: {result['brief_path']}")
        for warning in result["warnings"]:
            print(f"- warning: {warning}")
        for error in result["blocking_errors"]:
            print(f"- error: {error}")
        return 0 if result["allowed"] else 1

    if args.command == "chapter-brief-scaffold":
        try:
            output_path = (
                Path(args.output)
                if args.output
                else default_brief_path(args.book_id, args.chapter_number)
            )
            if output_path.exists() and not args.force:
                raise FileExistsError(f"Chapter brief already exists: {output_path}")
            scaffold = build_chapter_brief_scaffold(args.book_id, args.chapter_number)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(scaffold, encoding="utf-8")
            write_markdown_html_sidecar(
                output_path,
                f"Chapter {args.chapter_number} Brief",
                scaffold,
            )
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Wrote chapter brief scaffold: {output_path.as_posix()}")
        print(f"HTML review copy: {output_path.with_suffix('.html').as_posix()}")
        return 0

    if args.command == "chapter-brief-check":
        try:
            result = check_chapter_brief(args.book_id, args.chapter_number)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Chapter brief check: {result['status']}")
        for warning in result["warnings"]:
            print(f"- warning: {warning}")
        for error in result["errors"]:
            print(f"- error: {error}")
        return 0 if result["passed"] else 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
