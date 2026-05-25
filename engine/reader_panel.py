from pathlib import Path

from engine.html_utils import markdown_to_html_page
from engine.io_utils import write_json, write_text
from engine.paths import books_dir

BOOKS_DIR = books_dir()


def write_reader_panel_review_scaffold(
    book_id: str,
    chapter_number: int,
    force: bool = False,
) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    output = root / "reviews" / f"ch_{chapter_number:04d}" / "reader_panel_review.json"
    if output.exists() and not force:
        raise FileExistsError(f"Reader panel review already exists: {output}")

    data = _reader_panel_scaffold(book_id, chapter_number)
    write_json(output, data)
    write_text(output.with_suffix(".html"), _render_reader_panel_html(data))
    return output


def _reader_panel_scaffold(book_id: str, chapter_number: int) -> dict:
    return {
        "book_id": book_id,
        "chapter": chapter_number,
        "review_type": "simulated_reader_panel",
        "canon_status": "non_canon_feedback",
        "blocks_acceptance": False,
        "usage_note": (
            "Use this as auxiliary reader-reaction feedback. It does not approve, "
            "reject, or update canon by itself."
        ),
        "simulated_personas": [
            {
                "id": "payoff_reader",
                "label": "Payoff-focused reader",
                "cares_about": [
                    "visible gains",
                    "clear trade advantage",
                    "protagonist initiative",
                ],
                "likely_reaction": "",
                "risk": "",
                "suggested_fix": "",
            },
            {
                "id": "binge_reader",
                "label": "Binge and follow-up reader",
                "cares_about": [
                    "chapter-end pull",
                    "next action",
                    "unresolved pressure",
                ],
                "likely_reaction": "",
                "risk": "",
                "suggested_fix": "",
            },
            {
                "id": "setting_logic_reader",
                "label": "Setting and rules reader",
                "cares_about": [
                    "rule consistency",
                    "resource logic",
                    "economy and faction constraints",
                ],
                "likely_reaction": "",
                "risk": "",
                "suggested_fix": "",
            },
            {
                "id": "emotional_reader",
                "label": "Emotion and relationship reader",
                "cares_about": [
                    "character pressure",
                    "emotional payoff",
                    "relationship movement",
                ],
                "likely_reaction": "",
                "risk": "",
                "suggested_fix": "",
            },
            {
                "id": "dropoff_risk_reader",
                "label": "Drop-off risk reader",
                "cares_about": [
                    "slow openings",
                    "frontloaded explanation",
                    "unclear reward",
                ],
                "likely_reaction": "",
                "risk": "",
                "suggested_fix": "",
            },
        ],
        "aggregate_findings": {
            "strongest_hook": "",
            "biggest_dropoff_risk": "",
            "recommended_revision_priority": [],
            "notes_for_author_direction": [],
        },
    }


def _render_reader_panel_html(data: dict) -> str:
    chapter = data["chapter"]
    lines = [
        f"# Chapter {chapter} Reader Panel Review",
        "",
        f"- Review type: {data['review_type']}",
        f"- Canon status: {data['canon_status']}",
        f"- Blocks acceptance: {data['blocks_acceptance']}",
        "",
        "## Use",
        "",
        data["usage_note"],
        "",
        "## Simulated Personas",
        "",
    ]
    for persona in data["simulated_personas"]:
        lines.extend(
            [
                f"### {persona['label']}",
                "",
                f"- ID: {persona['id']}",
                f"- Cares about: {', '.join(persona['cares_about'])}",
                "- Likely reaction:",
                "- Risk:",
                "- Suggested fix:",
                "",
            ]
        )
    lines.extend(
        [
            "## Aggregate Findings",
            "",
            "- Strongest hook:",
            "- Biggest dropoff risk:",
            "- Recommended revision priority:",
            "- Notes for author direction:",
        ]
    )
    return markdown_to_html_page(
        f"Chapter {chapter} Reader Panel Review",
        "\n".join(lines),
    )
