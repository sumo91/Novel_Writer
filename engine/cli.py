import argparse
from pathlib import Path

from engine.acceptance_packet import draft_acceptance_packet
from engine.book_factory import create_book
from engine.chapter_acceptance import accept_chapter
from engine.context_builder import write_context
from engine.pipeline import (
    pipeline_accept,
    pipeline_draft_acceptance,
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

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
