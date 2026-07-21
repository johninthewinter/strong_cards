#!/usr/bin/env python3
"""Reject credentials, personal machine data, and private artifacts in public Git content."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AuditError(RuntimeError):
    """Raised when publication data violates the security boundary."""


def git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=not binary,
    )
    if result.returncode != 0:
        error = result.stderr.decode(errors="replace") if binary else result.stderr
        raise AuditError(f"git {' '.join(args)} failed: {error.strip()}")
    return result.stdout


def public_patterns() -> tuple[tuple[str, re.Pattern[str]], ...]:
    flags = re.IGNORECASE
    return (
        ("macOS user-home path", re.compile("/" + "Users" + r"/[^/\s\"']+")),
        ("Unix user-home path", re.compile("/" + "home" + r"/[^/\s\"']+")),
        ("Windows user-home path", re.compile(r"[A-Za-z]:\\" + "Users" + r"\\[^\\\s\"']+")),
        ("local file URI", re.compile("file" + r":/{2,3}", flags)),
        ("macOS temporary path", re.compile("/private/" + r"(?:tmp|var/folders)/[^\s\"']+")),
        ("generic temporary path", re.compile("/" + r"tmp/[^\s\"']+")),
        ("OpenAI-style secret", re.compile("s" + r"k-[A-Za-z0-9_-]{16,}")),
        ("GitHub token", re.compile("g" + r"h[pousr]_[A-Za-z0-9]{20,}")),
        ("GitHub fine-grained token", re.compile("github" + r"_pat_[A-Za-z0-9_]{20,}")),
        ("AWS access key", re.compile("A" + r"KIA[0-9A-Z]{16}")),
        ("Google API key", re.compile("A" + r"Iza[0-9A-Za-z_-]{30,}")),
        ("Slack token", re.compile("x" + r"ox[baprs]-[A-Za-z0-9-]{10,}")),
        ("bearer credential", re.compile("Bear" + r"er\s+[A-Za-z0-9._~+/-]{20,}", flags)),
        ("JWT credential", re.compile("e" + r"yJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
        ("private key", re.compile("-{5}" + r"BEGIN [A-Z ]*PRIVATE KEY-{5}", flags)),
        (
            "credential assignment",
            re.compile(
                r"\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)\b"
                r"\s*[:=]\s*[\"']?[A-Za-z0-9._~+/-]{12,}",
                flags,
            ),
        ),
        ("email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
        ("MAC address", re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")),
        ("private IPv4 address", re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))(?:\.\d{1,3}){2}\b")),
        (
            "labelled machine identifier",
            re.compile(
                r"\b(?:hardware\s+uuid|provisioning\s+udid|machine\s+id|serial\s+number)\b"
                r"\s*[:=]\s*[^\s,;]{4,}",
                flags,
            ),
        ),
    )


def inspect_text(label: str, data: bytes, findings: list[str]) -> None:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        findings.append(f"{label}: non-UTF-8 public file or historical blob")
        return

    for kind, pattern in public_patterns():
        if pattern.search(text):
            findings.append(f"{label}: contains {kind}")


def current_public_files(findings: list[str]) -> None:
    raw = git("ls-files", "-z", binary=True)
    assert isinstance(raw, bytes)
    paths = [Path(value.decode("utf-8")) for value in raw.split(b"\0") if value]
    if not paths:
        findings.append("index: no tracked public files")
        return

    forbidden_names = {".env", ".env.local", "id_rsa", "id_ed25519", "auth.json"}
    for relative in paths:
        label = f"tracked:{relative.as_posix()}"
        if ".private-inputs" in relative.parts:
            findings.append(f"{label}: private archive is tracked")
        if relative.name.lower() in forbidden_names or relative.suffix.lower() in {".pem", ".p12", ".key"}:
            findings.append(f"{label}: credential-bearing filename is forbidden")

        path = ROOT / relative
        if path.is_symlink():
            findings.append(f"{label}: symbolic links are forbidden in the publication")
            continue
        if not path.is_file():
            findings.append(f"{label}: tracked path is not a regular file")
            continue
        inspect_text(label, path.read_bytes(), findings)


def reachable_history(findings: list[str]) -> None:
    raw = git("rev-list", "--objects", "--all")
    assert isinstance(raw, str)
    objects: dict[str, str] = {}
    for line in raw.splitlines():
        object_id, _, path = line.partition(" ")
        if not path or object_id in objects:
            continue
        object_type = git("cat-file", "-t", object_id)
        assert isinstance(object_type, str)
        if object_type.strip() == "blob":
            objects[object_id] = path

    for object_id, path in objects.items():
        blob = git("cat-file", "blob", object_id, binary=True)
        assert isinstance(blob, bytes)
        inspect_text(f"history:{object_id[:12]}:{path}", blob, findings)


def commit_metadata(findings: list[str]) -> None:
    raw = git("log", "--all", "--format=%H%x00%an%x00%ae%x00%cn%x00%ce")
    assert isinstance(raw, str)
    for line in raw.splitlines():
        commit, author_name, author_email, committer_name, committer_email = line.split("\0")
        for role, name, email in (
            ("author", author_name, author_email),
            ("committer", committer_name, committer_email),
        ):
            if not name.strip():
                findings.append(f"commit:{commit[:12]}: missing {role} name")
            noreply_suffix = "@" + "users.noreply.github.com"
            if not email.endswith(noreply_suffix):
                findings.append(f"commit:{commit[:12]}: {role} email is not a GitHub noreply address")


def repository_boundary(findings: list[str]) -> None:
    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", ".private-inputs/README.md"],
        cwd=ROOT,
        check=False,
    )
    if ignored.returncode != 0:
        findings.append("boundary: .private-inputs is not protected by .gitignore")

    remotes = git("remote", "-v")
    assert isinstance(remotes, str)
    for line in remotes.splitlines():
        _name, url, *_rest = line.split()
        if re.search(r"https?://[^/\s]+@", url, re.IGNORECASE):
            findings.append("remote: HTTP remote URL contains user information or a credential")
        for kind, pattern in public_patterns():
            if "credential" in kind or "token" in kind or "secret" in kind or "access key" in kind or "API key" in kind:
                if pattern.search(url):
                    findings.append(f"remote: URL contains {kind}")


def main() -> int:
    findings: list[str] = []
    try:
        current_public_files(findings)
        reachable_history(findings)
        commit_metadata(findings)
        repository_boundary(findings)
    except (AuditError, OSError, ValueError) as error:
        print(f"PUBLICATION AUDIT FAILED: {error}", file=sys.stderr)
        return 1

    if findings:
        print("PUBLICATION AUDIT FAILED", file=sys.stderr)
        for finding in sorted(set(findings)):
            print(f"- {finding}", file=sys.stderr)
        return 1

    print("PUBLICATION AUDIT PASSED: tracked files, reachable history, commit metadata, and repository boundary are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
