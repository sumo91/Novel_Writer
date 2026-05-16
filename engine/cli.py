import argparse
from pathlib import Path

from engine.acceptance_packet import draft_acceptance_packet
from engine.book_factory import create_book
from engine.chapter_acceptance import accept_chapter
from engine.context_builder import write_context
from engine.drift_report import generate_drift_report
from engine.pending_approvals import (
    PendingApprovalNotFoundError,
    batch_update_pending_approvals,
    render_pending_approvals,
    sync_pending_approvals,
    update_pending_approval,
)
from engine.io_utils import read_yaml
from engine.pipeline import (
    pipeline_accept,
    pipeline_draft_acceptance,
    pipeline_quality_gate,
    pipeline_status,
    prepare_chapter,
)
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
        result = accept_chapter(args.book_id, Path(args.update_file), force=args.force)
        print(f"Accepted chapter: {result.chapter_path.as_posix()}")
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
        return 0

    if args.command == "prepare-chapter":
        paths = prepare_chapter(args.book_id, args.chapter_number, force=args.force)
        print(f"Prepared chapter pipeline: {paths.pipeline_dir.as_posix()}")
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
        return 0 if result["passed"] else 1

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

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
