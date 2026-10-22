#!/usr/bin/env python3
"""Scan a public repository tree for private-context locators.

The scanner uses only the known public Bridge Node 7 repository allowlist.
It never embeds or reveals a private-repository denylist.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import tempfile

PUBLIC_REPOS = frozenset({
    "Bridge-Node-7",
    "ai-cyber-assurance",
    "frontier-decision-engine",
    "frontier-intelligence-workflows",
    "frontier-mission-assurance",
    "materials-to-mission",
    "pax-silica",
    "quantum-readiness-space-communications",
})

ORG_LINK = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/Bridge-Node-7/([A-Za-z0-9_.-]+)", re.I
)
RAW_LINK = re.compile(
    r"(?:https?://)?raw\.githubusercontent\.com/Bridge-Node-7/([A-Za-z0-9_.-]+)", re.I
)
API_LINK = re.compile(
    r"(?:https?://)?api\.github\.com/repos/Bridge-Node-7/([A-Za-z0-9_.-]+)", re.I
)
SSH_LINK = re.compile(
    r"(?:ssh://)?git@github\.com[:/]Bridge-Node-7/([A-Za-z0-9_.-]+)", re.I
)
PUBLIC_REPOS_FOLDED = frozenset(name.casefold() for name in PUBLIC_REPOS)
PRIVATE_CONTEXT_PATTERNS = {
    "SANDBOX_PATH": re.compile(r"sandbox:/mnt/data/", re.I),
    "MNT_DATA_PATH": re.compile(r"(?<![A-Za-z0-9_])/mnt/data/", re.I),
    "USER_HOME_PATH": re.compile(r"(?:[A-Z]:[\\/](?:Users|Documents and Settings)[\\/][^\\/\s]+|/(?:Users|home)/[^/\s]+)", re.I),
    "CHATGPT_CONVERSATION": re.compile(r"https://chatgpt\.com/c/", re.I),
    "CHATGPT_PROJECT": re.compile(r"https://chatgpt\.com/g/g-p-", re.I),
    "CHATGPT_SHARED": re.compile(r"https://(?:chatgpt\.com|chat\.openai\.com)/share/", re.I),
    "CHATGPT_LEGACY_CONVERSATION": re.compile(r"https://chat\.openai\.com/(?:c/|g/)", re.I),
    "CONNECTOR_FILE_REF": re.compile(r"\bturn\d+file\d+\b", re.I),
    "INTERNAL_FILE_ID": re.compile(r"\bfile_[0-9a-f]{20,}\b", re.I),
}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build"}
SKIP_FILES = {"scripts/check_public_transfer_boundary.py"}
MAX_TEXT_BYTES = 2_000_000


def _iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if rel in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            if path.stat().st_size > MAX_TEXT_BYTES:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        yield rel, text


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    root = root.resolve()
    for rel, text in _iter_text_files(root):
        for pattern, label in (
            (ORG_LINK, "GITHUB"),
            (RAW_LINK, "RAW"),
            (API_LINK, "API"),
            (SSH_LINK, "SSH"),
        ):
            for match in pattern.finditer(text):
                if match.group(1).casefold().removesuffix(".git") not in PUBLIC_REPOS_FOLDED:
                    # Report category and file only. Never echo the target.
                    findings.append(f"NONPUBLIC_OR_UNKNOWN_{label}_LOCATOR:{rel}")
        for code, pattern in PRIVATE_CONTEXT_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{code}:{rel}")
    return sorted(set(findings))


def self_test() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "ok.md").write_text(
            "https://github.com/Bridge-Node-7/materials-to-mission\n"
            "https://raw.githubusercontent.com/Bridge-Node-7/frontier-mission-assurance/main/README.md\n",
            encoding="utf-8",
        )
        assert scan(root) == []

        (root / "bad.md").write_text(
            "https://github.com/Bridge-Node-7/not-in-public-estate\n"
            "sandbox:/mnt/data/example.txt\n"
            "https://chatgpt.com/c/example\n"
            "https://chatgpt.com/share/example\n"
            "https://chat.openai.com/c/example\n"
            "C:/Users/example-user/private-notes.txt\n",
            encoding="utf-8",
        )
        findings = scan(root)
        assert any(x.startswith("NONPUBLIC_OR_UNKNOWN_GITHUB_LOCATOR") for x in findings)
        assert any(x.startswith("SANDBOX_PATH") for x in findings)
        assert any(x.startswith("CHATGPT_CONVERSATION") for x in findings)
        assert any(x.startswith("CHATGPT_SHARED") for x in findings)
        assert any(x.startswith("CHATGPT_LEGACY_CONVERSATION") for x in findings)
        assert any(x.startswith("USER_HOME_PATH") for x in findings)

        (root / "bad.md").write_text(
            "https://API.GITHUB.COM/repos/bridge-node-7/not-in-public-estate\n"
            "git@github.com:Bridge-Node-7/not-in-public-estate.git\n"
            "https://GITHUB.COM/bridge-node-7/not-in-public-estate/issues/1\n"
            "https://RAW.GITHUBUSERCONTENT.COM/bridge-node-7/not-in-public-estate/main/README.md\n",
            encoding="utf-8",
        )
        findings = scan(root)
        for kind in ("API", "SSH", "GITHUB", "RAW"):
            assert any(x.startswith(f"NONPUBLIC_OR_UNKNOWN_{kind}_LOCATOR") for x in findings)
        assert all("not-in-public-estate" not in x for x in findings)

        (root / "bad.md").write_text(
            "https://API.GITHUB.COM/repos/bridge-node-7/MATERIALS-TO-MISSION\n"
            "git@github.com:Bridge-Node-7/materials-to-mission.git\n",
            encoding="utf-8",
        )
        assert scan(root) == []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--label", default="repository")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        print("PASS public transfer boundary self-test")
        return 0

    findings = scan(args.root)
    state = "PASS" if not findings else "SAFE_STOP"
    print(f"PUBLIC_TRANSFER_BOUNDARY label={args.label} state={state} findings={len(findings)}")
    # Public CI logs must not echo paths, identifiers, or matched content.
    # Local reviewers may use scan() to inspect filenames in a protected environment.
    for category in sorted({finding.partition(":")[0] for finding in findings}):
        print("CHECK:", category)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
