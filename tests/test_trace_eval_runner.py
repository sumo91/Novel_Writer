from engine import cli, trace_eval_runner
from engine.io_utils import read_json, write_yaml


def test_run_trace_eval_suite_checks_fixture_response_and_file_events(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "traces"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "showrunner.yaml",
        {
            "id": "showrunner",
            "description": "Showrunner trace fixtures.",
            "cases": [
                {
                    "id": "raw-idea-gate",
                    "prompt": "我想开一本轻松经营向带系统的新书。",
                    "mode": "fixture",
                    "fixture": {
                        "final_response": "当前是 Raw Idea 阶段。下一步先做新书 kickoff。你更想要哪种经营场景？",
                        "file_events": [],
                    },
                    "expect": {
                        "response_contains": ["Raw Idea", "新书 kickoff"],
                        "response_not_contains": ["第一章正文"],
                        "files_created": [],
                        "files_not_created_under": ["books/"],
                    },
                }
            ],
        },
    )

    result = trace_eval_runner.run_trace_eval_suite("showrunner")

    assert result["passed"] is True
    assert result["summary"]["passed"] == 1
    assert result["cases"][0]["passed"] is True
    report = read_json(tmp_path / "reports" / "trace_evals" / "showrunner.json")
    assert report["cases"][0]["id"] == "raw-idea-gate"


def test_run_trace_eval_suite_reports_response_and_file_boundary_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "traces"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "failure.yaml",
        {
            "id": "failure",
            "cases": [
                {
                    "id": "bad-trace",
                    "mode": "fixture",
                    "fixture": {
                        "final_response": "我已经写好第一章正文。",
                        "file_events": [
                            {"action": "create", "path": "books/bad/chapter.md"},
                        ],
                    },
                    "expect": {
                        "response_contains": ["Raw Idea"],
                        "response_not_contains": ["第一章正文"],
                        "files_created": [],
                        "files_not_created_under": ["books/"],
                    },
                }
            ],
        },
    )

    result = trace_eval_runner.run_trace_eval_suite("failure")

    assert result["passed"] is False
    errors = result["cases"][0]["errors"]
    assert "response missing: Raw Idea" in errors
    assert "response unexpectedly contained: 第一章正文" in errors
    assert "unexpected file creation: books/bad/chapter.md" in errors
    assert "unexpected file creation under books/: books/bad/chapter.md" in errors


def test_run_trace_eval_suite_supports_response_contains_any(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "traces"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "any.yaml",
        {
            "id": "any",
            "cases": [
                {
                    "id": "any-pass",
                    "mode": "fixture",
                    "fixture": {"final_response": "Stop at the concept gate.", "file_events": []},
                    "expect": {
                        "response_contains_any": [["概念门", "concept gate", "kickoff gate"]]
                    },
                },
                {
                    "id": "any-fail",
                    "mode": "fixture",
                    "fixture": {"final_response": "No matching phrase.", "file_events": []},
                    "expect": {
                        "response_contains_any": [["Raw Idea", "原始想法"]]
                    },
                },
            ],
        },
    )

    result = trace_eval_runner.run_trace_eval_suite("any")

    assert result["passed"] is False
    assert result["cases"][0]["passed"] is True
    assert result["cases"][1]["errors"] == [
        "response missing any of: Raw Idea | 原始想法"
    ]


def test_run_trace_eval_suite_does_not_treat_modify_as_creation(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "traces"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "modify.yaml",
        {
            "id": "modify",
            "cases": [
                {
                    "id": "modify-only",
                    "mode": "fixture",
                    "fixture": {
                        "final_response": "modified tests only",
                        "file_events": [
                            {"action": "modify", "path": "tests/test_eval_runner.py"},
                        ],
                    },
                    "expect": {
                        "response_contains": ["modified tests only"],
                        "files_created": [],
                        "files_not_created_under": ["books/"],
                    },
                }
            ],
        },
    )

    result = trace_eval_runner.run_trace_eval_suite("modify")

    assert result["passed"] is True


def test_run_trace_eval_suite_requires_explicit_live_opt_in(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "traces"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "live.yaml",
        {
            "id": "live",
            "cases": [
                {
                    "id": "live-case",
                    "mode": "live",
                    "prompt": "Say Raw Idea.",
                    "expect": {"response_contains": ["Raw Idea"]},
                }
            ],
        },
    )

    result = trace_eval_runner.run_trace_eval_suite("live")

    assert result["passed"] is False
    assert result["cases"][0]["errors"] == ["live trace eval requires --live"]


def test_run_trace_eval_suite_can_run_live_case_with_injected_runner(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "traces"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "live.yaml",
        {
            "id": "live",
            "cases": [
                {
                    "id": "live-case",
                    "mode": "live",
                    "prompt": "我想开一本轻松经营向带系统的新书。",
                    "expect": {
                        "response_contains": ["Raw Idea", "不会创建文件"],
                        "files_created": [],
                        "files_not_created_under": ["books/"],
                    },
                }
            ],
        },
    )
    calls = []

    def fake_live_runner(case, workspace_root):
        calls.append((case["id"], workspace_root.name))
        return {
            "final_response": "Raw Idea 阶段，我不会创建文件。",
            "file_events": [],
            "stdout": '{"type":"message","role":"assistant"}\n',
            "stderr": "",
            "exit_code": 0,
        }

    result = trace_eval_runner.run_trace_eval_suite(
        "live",
        allow_live=True,
        live_runner=fake_live_runner,
    )

    assert result["passed"] is True
    assert calls[0][0] == "live-case"
    assert calls[0][1].startswith("live-case_")
    case = result["cases"][0]
    assert case["mode"] == "live"
    assert case["exit_code"] == 0
    assert case["passed"] is True


def test_codex_live_runner_reports_permission_error_without_traceback(tmp_path, monkeypatch):
    case = {"id": "live-case", "prompt": "Say ok."}

    def raise_permission_error(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(trace_eval_runner.subprocess, "run", raise_permission_error)
    monkeypatch.setattr(trace_eval_runner.shutil, "which", lambda name: "codex.ps1")

    result = trace_eval_runner._run_codex_live_case(case, tmp_path)

    assert result["exit_code"] == 1
    assert "PermissionError" in result["stderr"]
    assert "denied" in result["stderr"]


def test_codex_live_runner_prefers_cmd_shim_on_windows(tmp_path, monkeypatch):
    case = {"id": "live-case", "prompt": "Say ok."}
    seen = {}

    class Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen["input"] = kwargs.get("input")
        return Completed()

    def fake_which(name):
        return {"codex.cmd": "C:/bin/codex.cmd", "codex": "C:/bin/codex.ps1"}.get(name)

    monkeypatch.setattr(trace_eval_runner.subprocess, "run", fake_run)
    monkeypatch.setattr(trace_eval_runner.shutil, "which", fake_which)

    result = trace_eval_runner._run_codex_live_case(case, tmp_path)

    assert result["exit_code"] == 0
    assert seen["command"][0] == "C:/bin/codex.cmd"
    assert "--sandbox" in seen["command"]
    assert "workspace-write" in seen["command"]
    assert seen["command"][-1] == "-"
    assert "Say ok." in seen["input"]


def test_codex_live_runner_reports_timeout_without_traceback(tmp_path, monkeypatch):
    case = {"id": "live-case", "prompt": "Say ok.", "live": {"timeout_seconds": 3}}

    def raise_timeout(command, **kwargs):
        raise trace_eval_runner.subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

    monkeypatch.setattr(trace_eval_runner.subprocess, "run", raise_timeout)
    monkeypatch.setattr(trace_eval_runner, "_codex_executable", lambda: "codex.cmd")

    result = trace_eval_runner._run_codex_live_case(case, tmp_path)

    assert result["exit_code"] == 124
    assert "timed out after 3 seconds" in result["stderr"]


def test_build_live_prompt_directs_model_to_answer_current_prompt():
    prompt = trace_eval_runner._build_live_prompt({"prompt": "帮我写第一章。"})

    assert "Answer the user prompt below now." in prompt
    assert "帮我写第一章。" in prompt
    assert "later prompt" not in prompt


def test_live_workspace_uses_unique_run_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)

    first = trace_eval_runner._prepare_live_workspace("case", {})
    second = trace_eval_runner._prepare_live_workspace("case", {})

    assert first != second
    assert first.name.startswith("case_")
    assert second.name.startswith("case_")


def test_trace_eval_cli_lists_and_runs_suites(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "traces"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "demo.yaml",
        {
            "id": "demo",
            "description": "Demo trace eval.",
            "cases": [
                {
                    "id": "ok",
                    "mode": "fixture",
                    "fixture": {"final_response": "ok", "file_events": []},
                    "expect": {"response_contains": ["ok"]},
                }
            ],
        },
    )

    list_result = cli.main(["list-trace-evals"])
    run_result = cli.main(["run-trace-evals", "demo"])

    captured = capsys.readouterr()
    assert list_result == 0
    assert run_result == 0
    assert "- demo: Demo trace eval. (1 cases)" in captured.out
    assert "Trace eval suite: demo" in captured.out


def test_trace_eval_cli_live_flag_passes_opt_in(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(trace_eval_runner, "PROJECT_ROOT", tmp_path)
    suite_dir = tmp_path / "evals" / "traces"
    suite_dir.mkdir(parents=True)
    write_yaml(
        suite_dir / "live.yaml",
        {
            "id": "live",
            "cases": [
                {
                    "id": "needs-live",
                    "mode": "live",
                    "prompt": "Say ok.",
                    "expect": {"response_contains": ["ok"]},
                }
            ],
        },
    )

    def fake_run_trace_eval_suite(suite_id, allow_live=False, live_runner=None):
        assert suite_id == "live"
        assert allow_live is True
        assert live_runner is None
        return {
            "suite_id": "live",
            "passed": True,
            "summary": {"total": 1, "passed": 1, "failed": 0},
        }

    monkeypatch.setattr(cli, "run_trace_eval_suite", fake_run_trace_eval_suite)

    result = cli.main(["run-trace-evals", "live", "--live"])

    captured = capsys.readouterr()
    assert result == 0
    assert "Trace eval suite: live" in captured.out
