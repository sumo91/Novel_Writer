# Eval Testing

Use deterministic eval suites to check workflow behavior that should remain stable across system changes.

These evals are not LLM-judged literary quality tests. They are offline command-and-expectation checks for core workflow contracts, CLI behavior, and regression-sensitive outputs.

## Commands

```powershell
python -m engine.cli list-evals
python -m engine.cli run-evals workflow_smoke
python -m engine.cli run-evals showrunner_static
python -m engine.cli run-evals knowledge_card_quality
python -m engine.cli run-evals new_book_dynamic
python -m engine.cli run-evals chapter_pipeline_dynamic
python -m engine.cli list-trace-evals
python -m engine.cli run-trace-evals showrunner_new_book
python -m engine.cli run-trace-evals showrunner_live_smoke --live
```

Reports are written to:

- `reports/evals/<suite_id>.json`
- `reports/evals/<suite_id>.md`
- `reports/trace_evals/<suite_id>.json`
- `reports/trace_evals/<suite_id>.md`

## Suite Format

Eval suites live in `evals/suites/*.yaml`.

```yaml
id: workflow_smoke
description: Deterministic smoke evals for core workflow commands.
cases:
  - id: cli_help_lists_eval_commands
    command:
      - --help
    expect:
      exit_code: 0
      stdout_contains:
        - run-evals
```

Dynamic suites use `steps` instead of a single `command`. Each dynamic case runs inside an isolated workspace under `.tmp/eval_workspaces/<case_id>`.

```yaml
id: new_book_dynamic
cases:
  - id: init_book_to_concept_review
    workspace:
      copy:
        - engine
        - knowledge
    steps:
      - id: init-book
        command:
          - python
          - -m
          - engine.cli
          - init-book
          - __eval_dynamic_book__
          - --title
          - Eval Dynamic Book
        expect:
          exit_code: 0
          files_exist:
            - books/__eval_dynamic_book__/book.yaml
```

Dynamic steps can also write fixture files directly:

```yaml
steps:
  - id: write-fixtures
    write_files:
      - path: books/demo/drafts/ch_0001_final_candidate.md
        content: |
          Final candidate text.
      - path: books/demo/reviews/ch_0001/prose_quality_review.json
        json:
          score: 88
      - path: books/demo/authoring/ch_0001_author_direction.yaml
        yaml:
          approved_for_final_candidate: true
```

Supported expectations:

- `exit_code`
- `stdout_contains`
- `stdout_not_contains`
- `stderr_contains`
- `files_exist`
- `files_not_exist`
- `file_contains`
- `file_not_contains`
- `line_count_max`
- `line_count_min`

`file_contains` and `file_not_contains` map repository-relative file paths to lists of required or forbidden text:

```yaml
expect:
  file_contains:
    AGENTS.md:
      - constitution layer
  file_not_contains:
    .agents/skills/novel-writing-showrunner/SKILL.md:
      - "### Required Phases"
  line_count_max:
    AGENTS.md: 180
```

For dynamic step checks, file expectations are relative to the isolated eval workspace. For single-command static checks, file expectations are relative to the repository root.

Dynamic cases stop after the first failed step. Later steps are reported as skipped so the failure report points at the first broken workflow boundary.

## Trace Eval Format

Trace eval suites live in `evals/traces/*.yaml`.

Trace Eval v0 uses fixture traces. It does not call a live LLM by default. A fixture contains the prompt, final response, and file events that should be checked against behavior expectations.

```yaml
id: showrunner_new_book
cases:
  - id: raw_idea_discussion_gate
    prompt: 我想开一本轻松经营向带系统的新书，具体设定还没想好。
    mode: fixture
    fixture:
      final_response: |
        当前是 Raw Idea 阶段，下一步应该走新书 kickoff 讨论门。
        我不会先创建书籍文件、写大纲或写正文。
      file_events: []
    expect:
      response_contains:
        - Raw Idea
        - 新书 kickoff
      response_not_contains:
        - 第一章正文
      files_created: []
      files_not_created_under:
        - books/
```

Supported trace expectations:

- `response_contains`
- `response_contains_any`
- `response_not_contains`
- `files_created`
- `files_not_created_under`

`response_contains_any` takes a list of option groups. Each group passes when at least one option appears in the final response:

```yaml
expect:
  response_contains_any:
    - [gate, 门, concept, 概念]
```

Use trace evals for process behavior: routing, approval-boundary language, refusal to skip gates, and whether the agent created files where it should not.

Do not treat fixture traces as proof that a live model will always behave the same way. They are regression fixtures for expected behavior shape. Live `codex exec --json` trace capture should be added as a separate explicit mode after the fixture checks are stable.

Trace evals can also include explicit live cases:

```yaml
id: showrunner_live_smoke
cases:
  - id: live_raw_idea_discussion_gate
    mode: live
    prompt: 我想开一本轻松经营向带系统的新书，具体设定还没想好。
    workspace:
      copy:
        - AGENTS.md
        - .agents
        - docs/workflows/v5-0-new-book-kickoff.md
    expect:
      response_not_contains:
        - 第一章正文
      files_created: []
      files_not_created_under:
        - books/
```

Live cases are refused unless the command includes `--live`:

```powershell
python -m engine.cli run-trace-evals showrunner_live_smoke --live
```

Live mode runs `codex exec --json` inside `.tmp/trace_eval_workspaces/<case_id>` with a read-only sandbox and writes the final assistant message into that workspace before checking expectations. Use live mode sparingly because it depends on model behavior, local Codex configuration, and available authentication.

## Current Scope

Use evals for stable deterministic behavior:

- CLI command surfaces;
- clean failure messages;
- workflow smoke checks;
- required report or artifact generation;
- static architecture contracts that should not drift, such as AGENTS as constitution layer, the showrunner skill as routing layer, and runbooks as detailed procedures.
- isolated dynamic workflow behavior, such as creating a temporary book project, scaffolding a craft contract, generating a concept review, and validating the result.
- full mechanical chapter-pipeline behavior, such as preparing a chapter, checking quality gates, drafting an acceptance packet, accepting the chapter, and validating the book.
- reusable craft-card hygiene, including required structure, concise actionable principles, non-empty checks, non-empty failure modes, and anti-dump guardrails.

Current suites:

- `workflow_smoke`: CLI and failure-message smoke checks.
- `showrunner_static`: static checks that keep AGENTS, the showrunner skill, and the new-book runbook in their intended layers.
- `knowledge_card_quality`: isolated craft-card quality checks for schema, concision, and actionable checklist discipline.
- `new_book_dynamic`: isolated multi-step workflow check for the new-book setup and concept-gate artifact chain.
- `chapter_pipeline_dynamic`: isolated full mechanical single-chapter pipeline check from preparation through accepted chapter.
- `showrunner_new_book`: fixture trace checks for showrunner routing and approval-boundary behavior.
- `showrunner_live_smoke`: explicit live Codex trace regression pack for core showrunner routing behavior. Requires `--live`.

## Staged Roadmap

The eval system follows a staged shape inspired by skill eval practice: prompt or task input, execution trace or generated artifacts, deterministic checks where possible, and scoring/reporting.

1. Deterministic CLI evals: commands, exit codes, outputs, and generated reports.
2. Static architecture evals: file content, forbidden content, and size limits for core system documents.
3. Dynamic workflow evals: execute real CLI steps in `.tmp/eval_workspaces/` and inspect generated artifacts without polluting real book projects.
4. Fixture trace evals: check captured or hand-authored traces for routing, approval gates, response boundaries, and file-event boundaries.
5. Explicit live Codex trace evals: run representative prompts with `codex exec --json`, capture traces or artifacts, and check process constraints such as approval gates and file creation boundaries. These require `--live`.
6. Future rubric evals: use reviewed human or LLM scoring only for subjective concept, prose, humor, or reader-promise quality after enough accepted project examples exist.

Do not use this runner for subjective prose quality or live LLM judging yet. Those should remain separate reviewed eval layers until the deterministic architecture is stable.
