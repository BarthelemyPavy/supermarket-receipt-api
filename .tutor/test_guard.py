"""Test the tutor hooks with stdlib only, independently of the student's TD tests."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / ".tutor" / "guard.py"


class TutorGuardTests(unittest.TestCase):
    """Exercise hook decisions via subprocesses; no TD code is imported or modified."""

    def payload(self, tool_name: str, tool_input: dict) -> dict:
        """Return a PreToolUse payload for a named tool and its input dict, without I/O."""
        return {
            "hook_event_name": "PreToolUse",
            "cwd": str(ROOT),
            "tool_name": tool_name,
            "tool_input": tool_input,
        }

    def invoke(
        self,
        payload: dict | str,
        mode: str = "pre-tool",
        guard: Path = GUARD,
    ) -> subprocess.CompletedProcess:
        """Run a hook Path with dict/raw-str stdin and str mode; return captured process output."""
        raw = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.run(
            [sys.executable, "-I", "-B", str(guard), mode],
            input=raw,
            text=True,
            capture_output=True,
            check=False,
            cwd=guard.parent.parent,
            timeout=10,
        )

    def assert_allowed(self, payload: dict) -> None:
        """Assert a payload dict allows a tool silently; return None or raise AssertionError."""
        result = self.invoke(payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")
        self.assertEqual(result.stderr.strip(), "")

    def assert_denied(self, payload: dict | str, guard: Path = GUARD) -> None:
        """Assert a dict/raw-str payload is denied by guard Path; return None or raise."""
        result = self.invoke(payload, guard=guard)
        if result.returncode == 2:
            self.assertTrue(result.stderr.strip(), "Exit 2 must explain the refusal.")
            return
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.strip(), "The tool was allowed instead of denied.")
        output = json.loads(result.stdout)
        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["hookEventName"], "PreToolUse")
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertTrue(decision["permissionDecisionReason"].strip())

    def test_native_read_tools_allow_local_files(self) -> None:
        """With no parameters, verify local read tools; return None and perform hook subprocesses."""
        examples = [
            (
                "Read",
                {
                    "file_path": str(
                        ROOT / "src" / "supermarket_receipt_api" / "services" / "checkout.py"
                    )
                },
            ),
            ("Read", {"file_path": "src/supermarket_receipt_api/services/checkout.py"}),
            ("Glob", {"pattern": "src/supermarket_receipt_api/*.py"}),
            ("Glob", {"pattern": "*.py", "path": "src/supermarket_receipt_api"}),
            (
                "Grep",
                {"pattern": "def", "path": "src/supermarket_receipt_api/services/checkout.py"},
            ),
            ("Grep", {"pattern": "def", "path": "src/supermarket_receipt_api"}),
        ]
        for name, arguments in examples:
            with self.subTest(name=name, arguments=arguments):
                self.assert_allowed(self.payload(name, arguments))

    def test_allowed_shell_grammar(self) -> None:
        """With no parameters, test narrow shell read syntax; return None after hook subprocesses."""
        commands = [
            "pwd",
            "ls -- src/supermarket_receipt_api",
            "ls -la -- src/supermarket_receipt_api",
            "cat -- src/supermarket_receipt_api/services/checkout.py",
            "head -n 1 -- src/supermarket_receipt_api/services/checkout.py",
            "tail -n 2000 -- src/supermarket_receipt_api/services/checkout.py",
            "rg --no-config --files",
            "rg --no-config --files -- src/supermarket_receipt_api",
            "rg --no-config -n -- def src/supermarket_receipt_api/services/checkout.py",
            "rg --no-config -n -F -- def src/supermarket_receipt_api/services/checkout.py",
        ]
        for tool_name, key in [("Bash", "command"), ("exec_command", "cmd")]:
            for command in commands:
                with self.subTest(tool=tool_name, command=command):
                    self.assert_allowed(self.payload(tool_name, {key: command}))

    def test_write_tools_are_denied(self) -> None:
        """With no parameters, reject direct writes; return None without executing requested writes."""
        for name in ["Write", "Edit", "MultiEdit", "NotebookEdit", "apply_patch"]:
            with self.subTest(tool=name):
                self.assert_denied(
                    self.payload(
                        name,
                        {
                            "file_path": "src/supermarket_receipt_api/services/checkout.py",
                            "content": "change",
                        },
                    )
                )

    def test_unknown_tools_and_delegation_are_denied(self) -> None:
        """With no parameters, reject untrusted tools; return None without calling their operations."""
        for name in [
            "Agent",
            "Task",
            "spawn_agent",
            "send_message",
            "write_stdin",
            "mcp__filesystem__write_file",
            "mcp__filesystem__read_file",
            "unknown_tool",
        ]:
            with self.subTest(tool=name):
                self.assert_denied(self.payload(name, {}))

    def test_code_execution_and_mutating_commands_are_denied(self) -> None:
        """With no parameters, reject executable code and mutations; return None after guard calls."""
        for command in [
            "python3 -c pass",
            "uv run pytest -q",
            "pytest -q",
            "ruff check .",
            "git status",
            "git checkout -- src/supermarket_receipt_api/services/checkout.py",
            "touch src/supermarket_receipt_api/new.py",
            "rm src/supermarket_receipt_api/services/checkout.py",
            "sh -c pwd",
            "env cat -- src/supermarket_receipt_api/services/checkout.py",
            "command cat -- src/supermarket_receipt_api/services/checkout.py",
            "/bin/cat -- src/supermarket_receipt_api/services/checkout.py",
        ]:
            with self.subTest(command=command):
                self.assert_denied(self.payload("Bash", {"command": command}))

    def test_shell_operators_are_denied(self) -> None:
        """With no parameters, reject shell metacharacters; return None without running shell code."""
        for command in [
            "pwd; pwd",
            "pwd && pwd",
            "pwd | cat",
            "pwd > output.txt",
            "cat < src/supermarket_receipt_api/services/checkout.py",
            "cat -- $(pwd)/src/supermarket_receipt_api/services/checkout.py",
            "cat -- `pwd`/src/supermarket_receipt_api/services/checkout.py",
            "cat -- $HOME/file",
            "pwd\npwd",
            "pwd\r\npwd",
            "cat -- src/supermarket_receipt_api/checkout\\.py",
            "pwd &",
            "cat -- src/supermarket_receipt_api/{checkout,main}.py",
            "cat -- src/supermarket_receipt_api/checkout?.py",
            "cat -- ~root/file",
            "rg --no-config -n -- (def) src/supermarket_receipt_api",
        ]:
            with self.subTest(command=command):
                self.assert_denied(self.payload("Bash", {"command": command}))

    def test_shell_options_cannot_expand_permissions(self) -> None:
        """With no parameters, reject extra execution options; return None after isolated guard calls."""
        for name, arguments in [
            ("Bash", {"command": "pwd", "run_in_background": True}),
            ("Bash", {"command": "pwd", "dangerouslyDisableSandbox": True}),
            ("exec_command", {"cmd": "pwd", "shell": "/bin/sh"}),
            ("exec_command", {"cmd": "pwd", "tty": True}),
            ("exec_command", {"cmd": "pwd", "login": True}),
            ("exec_command", {"cmd": "pwd", "sandbox_permissions": "require_escalated"}),
            ("exec_command", {"cmd": "pwd", "workdir": "/private/tmp"}),
        ]:
            with self.subTest(tool=name, arguments=arguments):
                self.assert_denied(self.payload(name, arguments))

    def test_unapproved_read_options_are_denied(self) -> None:
        """With no parameters, reject extended command syntax; return None after guard subprocesses."""
        for command in [
            "ls -R -- src/supermarket_receipt_api",
            "cat src/supermarket_receipt_api/services/checkout.py",
            "head -n 0 -- src/supermarket_receipt_api/services/checkout.py",
            "head -n 2001 -- src/supermarket_receipt_api/services/checkout.py",
            "tail -f -- src/supermarket_receipt_api/services/checkout.py",
            "rg --files",
            "rg --no-config --pre python3 -n -- def app",
            "rg --no-config -n -L -- def app",
            "rg --no-config -n -- def -",
            "cat -- src/supermarket_receipt_api/*.py",
        ]:
            with self.subTest(command=command):
                self.assert_denied(self.payload("Bash", {"command": command}))

    def test_reads_outside_repository_are_denied(self) -> None:
        """With no parameters, reject external/traversal reads; return None after guard subprocesses."""
        examples = [
            ("Read", {"file_path": "/etc/hosts"}),
            ("Read", {"file_path": "../outside.txt"}),
            ("Glob", {"pattern": "../*"}),
            ("Glob", {"pattern": "{..,app}/*"}),
            ("Glob", {"pattern": "~/*"}),
            ("Glob", {"pattern": "*", "path": "/private/tmp"}),
            ("Grep", {"pattern": "text", "path": "../"}),
            ("Bash", {"command": "cat -- /etc/hosts"}),
            ("Bash", {"command": "ls -- ../"}),
            ("Bash", {"command": "rg --no-config --files -- /private/tmp"}),
        ]
        for name, arguments in examples:
            with self.subTest(tool=name, arguments=arguments):
                self.assert_denied(self.payload(name, arguments))

    def test_missing_files_are_denied(self) -> None:
        """With no parameters, reject absent file targets; return None without creating target files."""
        for name, arguments in [
            ("Read", {"file_path": "src/supermarket_receipt_api/no-such-tutor-fixture.py"}),
            ("Bash", {"command": "cat -- src/supermarket_receipt_api/no-such-tutor-fixture.py"}),
        ]:
            with self.subTest(tool=name):
                self.assert_denied(self.payload(name, arguments))

    def test_private_environment_paths_are_denied(self) -> None:
        """With no parameters, reject internal/environment reads; return None after guard calls."""
        for path in [".git", ".venv", ".pytest_cache", ".ruff_cache"]:
            with self.subTest(path=path):
                self.assert_denied(self.payload("Bash", {"command": f"ls -- {path}"}))

    def test_invalid_payloads_fail_closed(self) -> None:
        """With no parameters, deny malformed/schema-invalid payloads; return None after guard calls."""
        examples = [
            "",
            "{",
            "null",
            "[]",
            "{}",
            self.payload("Read", {}),
            self.payload("Read", {"file_path": 1}),
            self.payload("Read", {"filePath": "src/supermarket_receipt_api/services/checkout.py"}),
            self.payload("Bash", {"cmd": "pwd"}),
            self.payload("exec_command", {"command": "pwd"}),
            self.payload("Bash", {"command": ["pwd"]}),
            {
                "hook_event_name": "PostToolUse",
                "cwd": str(ROOT),
                "tool_name": "Bash",
                "tool_input": {"command": "pwd"},
            },
            {
                "hook_event_name": "PreToolUse",
                "cwd": str(ROOT),
                "tool_name": "Bash",
                "tool_input": [],
            },
        ]
        for payload in examples:
            with self.subTest(payload=payload):
                self.assert_denied(payload)

    def test_missing_or_external_cwd_is_denied(self) -> None:
        """With no parameters, reject invalid hook working directories; return None after guard calls."""
        for cwd in [None, "", "/private/tmp", "src/supermarket_receipt_api", 42]:
            payload = self.payload("Bash", {"command": "pwd"})
            if cwd is None:
                del payload["cwd"]
            else:
                payload["cwd"] = cwd
            with self.subTest(cwd=cwd):
                self.assert_denied(payload)

    def test_symlink_escape_is_denied(self) -> None:
        """With no parameters, test escaping symlinks in a temporary repo; return None and clean it."""
        with tempfile.TemporaryDirectory(prefix="tutor-guard-") as temporary:
            fixture = Path(temporary)
            repository = fixture / "repo"
            tutor = repository / ".tutor"
            tutor.mkdir(parents=True)
            guard = tutor / "guard.py"
            shutil.copy2(GUARD, guard)
            outside = fixture / "outside.txt"
            outside.write_text("external fixture\n", encoding="utf-8")
            (repository / "escaped.txt").symlink_to(outside)
            for name, arguments in [
                ("Read", {"file_path": "escaped.txt"}),
                ("Bash", {"command": "cat -- escaped.txt"}),
                ("Grep", {"pattern": "external", "path": "escaped.txt"}),
            ]:
                payload = self.payload(name, arguments)
                payload["cwd"] = str(repository)
                with self.subTest(tool=name):
                    self.assert_denied(payload, guard=guard)

    def test_session_start_supplies_tutor_context(self) -> None:
        """With no parameters, check SessionStart reminder; return None after an isolated hook call."""
        result = self.invoke(
            {"hook_event_name": "SessionStart", "cwd": str(ROOT)},
            mode="session-start",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        context = output["additionalContext"]
        self.assertIsInstance(context, str)
        self.assertIn("tuteur", context.lower())
        self.assertGreater(len(context), 80)


class TutorConfigurationTests(unittest.TestCase):
    """Check both assistant integrations without activating assistants or any project hooks."""

    def test_checked_in_hook_configurations(self) -> None:
        """With no parameters, verify synchronous catch-all guards; return None or raise on mismatch."""
        for relative_path in [".claude/settings.json", ".codex/hooks.json"]:
            with self.subTest(configuration=relative_path):
                configuration = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
                for event, mode in [
                    ("PreToolUse", "pre-tool"),
                    ("SessionStart", "session-start"),
                ]:
                    entries = configuration["hooks"][event]
                    self.assertTrue(entries)
                    matching_commands = []
                    for entry in entries:
                        if event == "PreToolUse":
                            self.assertIn(entry.get("matcher", ""), ["", "*", ".*"])
                        for hook in entry["hooks"]:
                            self.assertEqual(hook["type"], "command")
                            self.assertFalse(hook.get("async", False))
                            command = hook["command"]
                            if ".tutor/guard.py" in command and mode in command:
                                matching_commands.append(command)
                    self.assertTrue(matching_commands, f"Missing {event} guard in {relative_path}")
                    for command in matching_commands:
                        self.assertIn("-I", command)
                        self.assertIn("-B", command)


if __name__ == "__main__":
    unittest.main()
