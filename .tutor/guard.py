"""Enforce a read-only tutoring tool policy using only the Python standard library.

Run with ``pre-tool`` or ``session-start`` and a hook payload on standard input.
The script returns hook JSON on standard output; it never executes a requested tool.
It does not authenticate students or classify the content of model responses.
"""

import json
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = (
    "MODE TUTEUR ACTIF — Tu guides et relis, tu ne réalises pas le TD. "
    "Demande la tentative et le raisonnement, puis donne un indice ciblé à la fois. "
    "Pas de solution complète, de patch prêt à appliquer ou de corrigé fragmenté. "
    "Ne modifie aucun fichier et ne contourne pas les hooks. "
    "L'étudiant exécute lui-même ses commandes et partage leurs résultats. "
    "Lis AGENTS.md pour le cadre pédagogique."
)
DENIAL = (
    "Mode tuteur : outil ou commande non autorisé en lecture seule. "
    "Ne pas contourner ce refus par un autre outil, un script ou un sous-agent. "
    "Guide l'étudiant ; il écrit et exécute lui-même ses essais. "
    "Lectures possibles : Read/Glob/Grep, pwd, cat -- fichier, "
    "ls -la -- chemin, head -n 80 -- fichier, rg --no-config --files, "
    "rg --no-config -n -- motif chemin."
)
SHELL_FIELDS = {
    "command",
    "cmd",
    "description",
    "timeout",
    "run_in_background",
    "dangerouslyDisableSandbox",
    "workdir",
    "shell",
    "login",
    "max_output_tokens",
    "yield_time_ms",
    "tty",
    "sandbox_permissions",
    "justification",
    "prefix_rule",
}


def repository_path(value: str, cwd: Path, *, file_only: bool = False) -> Path:
    """Resolve a repository path without opening it or following external links.

    Args: value is a nonempty path string; cwd is an absolute repository Path;
    file_only requires a regular file instead of a file or directory.
    Returns the resolved Path. Raises TypeError, ValueError or OSError for an
    invalid, missing, external or excluded path. Does not modify the filesystem.
    """
    if not isinstance(value, str) or not value or "\x00" in value:
        raise TypeError("path must be a nonempty string without NUL characters")
    requested = Path(value)
    resolved = (requested if requested.is_absolute() else cwd / requested).resolve(strict=True)
    if not resolved.is_relative_to(ROOT):
        raise ValueError("path must remain inside the student repository")
    excluded = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
    for part in resolved.relative_to(ROOT).parts:
        if part in excluded or part == ".env" or part.startswith(".env."):
            raise ValueError("path must not target repository internals or local environment files")
    if file_only and not resolved.is_file():
        raise ValueError("path must identify an existing regular file")
    if not resolved.is_file() and not resolved.is_dir():
        raise ValueError("path must identify a regular file or directory")
    return resolved


def safe_pattern(value: str) -> None:
    """Validate a relative Glob pattern without reading any files.

    Args: value is a nonempty POSIX glob string. Returns None; raises TypeError
    or ValueError for an absolute pattern or parent traversal. No side effects.
    """
    if not isinstance(value, str) or not value:
        raise TypeError("pattern must be a nonempty string")
    if (
        Path(value).is_absolute()
        or ".." in Path(value).parts
        or any(char in value for char in "\\{}~")
    ):
        raise ValueError("pattern must be relative and must not traverse parent directories")


def safe_shell(tool_name: str, tool_input: dict, cwd: Path) -> bool:
    """Recognize a small grammar of finite, non-executing consultation commands.

    Args: tool_name is Bash or exec_command; tool_input is its exact argument
    object; cwd is the resolved current repository directory. Returns True only
    for supported read commands. Invalid schemas or paths raise explicit errors.
    No command is executed. Python, tests, Git, shell chains and scripts are denied.
    """
    if set(tool_input) - SHELL_FIELDS:
        return False
    if tool_input.get("run_in_background", False) is not False:
        return False
    if tool_input.get("dangerouslyDisableSandbox", False) is not False:
        return False
    if tool_input.get("tty", False) is not False:
        return False
    if tool_input.get("login", False) is not False:
        return False
    if tool_input.get("shell") is not None:
        return False
    if tool_input.get("sandbox_permissions", "use_default") != "use_default":
        return False
    if tool_input.get("prefix_rule") is not None:
        return False
    if "workdir" in tool_input:
        cwd = repository_path(tool_input["workdir"], cwd)
        if not cwd.is_dir():
            raise ValueError("workdir must identify a repository directory")
    # These are two documented tool schemas, not interchangeable field aliases.
    command_key = "command" if tool_name == "Bash" else "cmd"
    other_key = "cmd" if tool_name == "Bash" else "command"
    if other_key in tool_input:
        raise ValueError(f"{tool_name} expects only the {command_key} command field")
    command = tool_input[command_key]
    if not isinstance(command, str) or not command:
        raise TypeError(f"{command_key} must be a nonempty string")
    if any(char in command for char in ";|&><$`\\\n\r\x00~*?[]{}()!"):
        return False
    words = shlex.split(command, posix=True)
    if words == ["pwd"]:
        return True
    if len(words) in {3, 4} and words[:1] == ["ls"]:
        if words[:-1] not in (["ls", "--"], ["ls", "-la", "--"]):
            return False
        repository_path(words[-1], cwd)
        return True
    if len(words) == 3 and words[:2] == ["cat", "--"]:
        repository_path(words[-1], cwd, file_only=True)
        return True
    if len(words) == 5 and words[0] in {"head", "tail"}:
        if words[1] != "-n" or words[3] != "--" or not words[2].isascii():
            return False
        if not words[2].isdigit() or not 1 <= int(words[2]) <= 2000:
            return False
        repository_path(words[-1], cwd, file_only=True)
        return True
    if words == ["rg", "--no-config", "--files"]:
        return True
    if len(words) == 5 and words[:4] == ["rg", "--no-config", "--files", "--"]:
        repository_path(words[-1], cwd)
        return True
    if len(words) in {6, 7} and words[:3] == ["rg", "--no-config", "-n"]:
        expected = ["rg", "--no-config", "-n"]
        if len(words) == 7:
            expected.append("-F")
        expected.append("--")
        if words[:-2] != expected:
            return False
        repository_path(words[-1], cwd)
        return True
    return False


def can_read(payload: dict) -> bool:
    """Decide whether a PreToolUse payload requests an approved read operation.

    Args: payload is a hook object with hook_event_name, cwd, tool_name and
    tool_input. Returns a bool; invalid fields raise TypeError, KeyError,
    ValueError or OSError. The policy has no tool or filesystem side effects.
    Unknown tools, MCP tools, editing and delegation are denied by default.
    """
    if not isinstance(payload, dict):
        raise TypeError("hook payload must be a JSON object")
    if payload["hook_event_name"] != "PreToolUse":
        raise ValueError("hook_event_name must be PreToolUse")
    raw_cwd = payload["cwd"]
    if not isinstance(raw_cwd, str) or not Path(raw_cwd).is_absolute():
        raise ValueError("cwd must be an absolute repository directory path")
    cwd = repository_path(raw_cwd, ROOT)
    if not cwd.is_dir():
        raise ValueError("cwd must identify a repository directory")
    name = payload["tool_name"]
    arguments = payload["tool_input"]
    if not isinstance(name, str) or not name:
        raise TypeError("tool_name must be a nonempty string")
    if not isinstance(arguments, dict):
        raise TypeError("tool_input must be a JSON object")
    if name in {"Bash", "exec_command"}:
        return safe_shell(name, arguments, cwd)
    if name == "Read":
        repository_path(arguments["file_path"], cwd, file_only=True)
        return True
    if name in {"Glob", "Grep"}:
        repository_path(arguments.get("path", str(cwd)), cwd)
        if name == "Glob":
            safe_pattern(arguments["pattern"])
        elif not isinstance(arguments["pattern"], str):
            raise TypeError("Grep pattern must be a string")
        return True
    return False


def main() -> int:
    """Handle one hook invocation from CLI arguments and standard input.

    Args: no Python parameters; argv selects pre-tool or session-start, stdin
    supplies hook JSON. Returns process status 0 for a valid hook response, or
    2 on invalid input/initialization. Writes only stdout/stderr, never files.
    An approved read returns no decision and preserves normal assistant approvals.
    """
    try:
        if len(sys.argv) != 2 or sys.argv[1] not in {"pre-tool", "session-start"}:
            raise ValueError("expected exactly one mode: pre-tool or session-start")
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise TypeError("hook payload must be a JSON object")
        if sys.argv[1] == "session-start":
            if payload["hook_event_name"] != "SessionStart":
                raise ValueError("hook_event_name must be SessionStart")
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "SessionStart",
                            "additionalContext": CONTEXT,
                        }
                    },
                    ensure_ascii=False,
                )
            )
        elif not can_read(payload):
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": DENIAL,
                        }
                    },
                    ensure_ascii=False,
                )
            )
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f"Mode tuteur : entrée invalide, opération refusée : {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
