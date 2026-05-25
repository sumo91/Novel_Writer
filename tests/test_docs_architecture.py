from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _line_count(relative_path: str) -> int:
    return len(_read(relative_path).splitlines())


def test_core_docs_keep_layer_boundaries():
    agents = _read("AGENTS.md")
    skill = _read(".agents/skills/novel-writing-showrunner/SKILL.md")
    runbook = _read("docs/workflows/v5-0-new-book-kickoff.md")

    assert "AGENTS.md is the constitution layer." in agents
    assert "Showrunner skill is the routing layer." in skill
    assert "This runbook is the detailed source of truth for new-book kickoff." in runbook


def test_core_docs_stay_compact_enough_to_remain_scannable():
    assert _line_count("AGENTS.md") <= 180
    assert _line_count(".agents/skills/novel-writing-showrunner/SKILL.md") <= 180


def test_showrunner_routes_to_runbook_instead_of_duplicating_new_book_details():
    skill = _read(".agents/skills/novel-writing-showrunner/SKILL.md")

    assert "docs/workflows/v5-0-new-book-kickoff.md" in skill
    assert "### Required Phases" not in skill
    assert "### Phase A" not in skill


def test_project_status_is_not_embedded_in_agents_rulebook():
    agents = _read("AGENTS.md")
    status = _read("docs/project_status.md")

    assert "## Current Project Facts" not in agents
    assert "xiuxian_shop_pilot" in status
