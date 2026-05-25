from engine import cli, eval_runner
from engine.io_utils import read_json, read_yaml, write_yaml


def test_run_eval_suite_executes_cli_cases_and_writes_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "smoke.yaml",
        {
            "id": "smoke",
            "description": "Basic command smoke eval.",
            "cases": [
                {
                    "id": "help",
                    "command": ["--help"],
                    "expect": {
                        "exit_code": 0,
                        "stdout_contains": ["usage:", "init-book"],
                    },
                }
            ],
        },
    )

    result = eval_runner.run_eval_suite("smoke")

    assert result["passed"] is True
    assert result["summary"]["passed"] == 1
    assert result["cases"][0]["passed"] is True
    report = tmp_path / "reports" / "evals" / "smoke.json"
    markdown = tmp_path / "reports" / "evals" / "smoke.md"
    assert report.exists()
    assert markdown.exists()
    assert read_json(report)["summary"]["passed"] == 1
    assert "# Eval Suite: smoke" in markdown.read_text(encoding="utf-8")


def test_run_eval_suite_reports_failed_expectation(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "failure.yaml",
        {
            "id": "failure",
            "cases": [
                {
                    "id": "missing-output",
                    "command": ["--help"],
                    "expect": {"stdout_contains": ["not in help"]},
                }
            ],
        },
    )

    result = eval_runner.run_eval_suite("failure")

    assert result["passed"] is False
    assert result["summary"]["failed"] == 1
    assert "stdout missing: not in help" in result["cases"][0]["errors"]


def test_run_eval_suite_checks_file_content_expectations(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    target = tmp_path / "docs" / "sample.md"
    target.parent.mkdir(parents=True)
    target.write_text("constitution layer\nrouting layer\n", encoding="utf-8")
    write_yaml(
        suite_dir / "file_content.yaml",
        {
            "id": "file_content",
            "cases": [
                {
                    "id": "checks-static-file-content",
                    "command": ["--help"],
                    "expect": {
                        "exit_code": 0,
                        "file_contains": {"docs/sample.md": ["constitution layer"]},
                        "file_not_contains": {"docs/sample.md": ["### Required Phases"]},
                    },
                }
            ],
        },
    )

    result = eval_runner.run_eval_suite("file_content")

    assert result["passed"] is True
    assert result["cases"][0]["errors"] == []


def test_run_eval_suite_reports_file_content_and_line_count_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    target = tmp_path / "docs" / "bloated.md"
    target.parent.mkdir(parents=True)
    target.write_text("alpha\nforbidden\nomega\n", encoding="utf-8")
    write_yaml(
        suite_dir / "static_failures.yaml",
        {
            "id": "static_failures",
            "cases": [
                {
                    "id": "reports-static-file-failures",
                    "command": ["--help"],
                    "expect": {
                        "file_contains": {"docs/bloated.md": ["missing"]},
                        "file_not_contains": {"docs/bloated.md": ["forbidden"]},
                        "line_count_max": {"docs/bloated.md": 2},
                        "line_count_min": {"docs/bloated.md": 4},
                    },
                }
            ],
        },
    )

    result = eval_runner.run_eval_suite("static_failures")

    assert result["passed"] is False
    errors = result["cases"][0]["errors"]
    assert "docs/bloated.md missing text: missing" in errors
    assert "docs/bloated.md unexpectedly contained text: forbidden" in errors
    assert "docs/bloated.md line_count expected <= 2, got 3" in errors
    assert "docs/bloated.md line_count expected >= 4, got 3" in errors


def test_run_eval_suite_executes_steps_in_isolated_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    source = tmp_path / "fixture"
    source.mkdir()
    (source / "seed.txt").write_text("seed\n", encoding="utf-8")
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "dynamic.yaml",
        {
            "id": "dynamic",
            "cases": [
                {
                    "id": "runs-multiple-steps",
                    "workspace": {
                        "copy": ["fixture"],
                    },
                    "steps": [
                        {
                            "id": "read-seed",
                            "command": [
                                "python",
                                "-c",
                                "from pathlib import Path; print(Path('fixture/seed.txt').read_text())",
                            ],
                            "expect": {"exit_code": 0, "stdout_contains": ["seed"]},
                        },
                        {
                            "id": "write-output",
                            "command": [
                                "python",
                                "-c",
                                "from pathlib import Path; Path('fixture/out.txt').write_text('done\\n')",
                            ],
                            "expect": {
                                "exit_code": 0,
                                "files_exist": ["fixture/out.txt"],
                                "file_contains": {"fixture/out.txt": ["done"]},
                            },
                        },
                    ],
                }
            ],
        },
    )

    result = eval_runner.run_eval_suite("dynamic")

    assert result["passed"] is True
    assert result["cases"][0]["passed"] is True
    assert result["cases"][0]["steps"][0]["id"] == "read-seed"
    assert result["cases"][0]["steps"][1]["id"] == "write-output"
    assert not (tmp_path / "fixture" / "out.txt").exists()
    report = read_json(tmp_path / "reports" / "evals" / "dynamic.json")
    assert report["cases"][0]["steps"][1]["passed"] is True


def test_run_eval_suite_reports_failed_dynamic_step_and_skips_later_steps(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "dynamic_failure.yaml",
        {
            "id": "dynamic_failure",
            "cases": [
                {
                    "id": "stops-after-failed-step",
                    "steps": [
                        {
                            "id": "fail",
                            "command": ["python", "-c", "print('bad')"],
                            "expect": {"stdout_contains": ["good"]},
                        },
                        {
                            "id": "skip-me",
                            "command": ["python", "-c", "print('should not run')"],
                        },
                    ],
                }
            ],
        },
    )

    result = eval_runner.run_eval_suite("dynamic_failure")

    assert result["passed"] is False
    steps = result["cases"][0]["steps"]
    assert steps[0]["passed"] is False
    assert "stdout missing: good" in steps[0]["errors"]
    assert steps[1]["passed"] is False
    assert steps[1]["skipped"] is True
    assert steps[1]["errors"] == ["skipped after previous step failed"]


def test_run_eval_suite_write_files_step_creates_workspace_fixtures(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "write_files.yaml",
        {
            "id": "write_files",
            "cases": [
                {
                    "id": "writes-fixtures",
                    "steps": [
                        {
                            "id": "write-fixture-files",
                            "write_files": [
                                {
                                    "path": "fixture/a.txt",
                                    "content": "alpha\n",
                                },
                                {
                                    "path": "fixture/data.json",
                                    "json": {"ok": True},
                                },
                                {
                                    "path": "fixture/data.yaml",
                                    "yaml": {"name": "demo"},
                                },
                            ],
                            "expect": {
                                "files_exist": [
                                    "fixture/a.txt",
                                    "fixture/data.json",
                                    "fixture/data.yaml",
                                ],
                                "file_contains": {
                                    "fixture/a.txt": ["alpha"],
                                    "fixture/data.json": ['"ok": true'],
                                    "fixture/data.yaml": ["name: demo"],
                                },
                            },
                        }
                    ],
                }
            ],
        },
    )

    result = eval_runner.run_eval_suite("write_files")

    assert result["passed"] is True
    assert result["cases"][0]["steps"][0]["passed"] is True
    assert not (tmp_path / "fixture").exists()


def test_list_eval_suites_reads_suite_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "demo.yaml",
        {"id": "demo", "description": "Demo eval.", "cases": []},
    )

    suites = eval_runner.list_eval_suites()

    assert suites == [{"id": "demo", "description": "Demo eval.", "cases": 0}]


def test_run_evals_cli_reports_result(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "suites"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "smoke.yaml",
        {
            "id": "smoke",
            "cases": [{"id": "help", "command": ["--help"], "expect": {"exit_code": 0}}],
        },
    )

    result = cli.main(["run-evals", "smoke"])

    captured = capsys.readouterr()
    assert result == 0
    assert "Eval suite: smoke" in captured.out
    assert "- passed: 1" in captured.out


def test_eval_suite_fixture_is_valid():
    suite = read_yaml(eval_runner.PROJECT_ROOT / "evals" / "suites" / "workflow_smoke.yaml")

    assert suite["id"] == "workflow_smoke"
    assert suite["cases"]
