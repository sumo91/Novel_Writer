import argparse
from pathlib import Path

from engine.book_factory import create_book
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

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
