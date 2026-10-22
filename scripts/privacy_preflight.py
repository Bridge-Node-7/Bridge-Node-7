#!/usr/bin/env python3
"""Public-source privacy preflight. Never echo matched private data.

Review newly added lines, paths, commit author metadata and PR text.
Policy is heuristic; no claim of universal PII detection or history sanitization.
"""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys

PATTERNS = {
    "personal-email": re.compile(r"(?i)(?<![a-z0-9._%+-])[a-z0-9._%+-]+@(?:gmail|yahoo|ymail|hotmail|outlook|icloud|protonmail|proton|aol|live|me)\.(?:com|net|org|me)"),
    "phone-number": re.compile(r"(?<!\d)(?:\+1[\s.-]?)?\(?[2-9]\d{2}\)?[\s.-][2-9]\d{2}[\s.-]\d{4}(?!\d)"),
    "local-home-path": re.compile(r"(?i)(?:[a-z]:[\\/](?:users|documents and settings)[\\/][^\\/\s]+|/(?:users|home)/[a-z0-9_.-]+)"),
    "private-key": re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA|ENCRYPTED|PGP )?PRIVATE KEY-----"),
    "github-token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{40,}"),
    "service-credential": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\bxox[baprs]-[A-Za-z0-9-]{15,}|\bsk-(?:proj-)?[A-Za-z0-9_-]{25,}\b"),
}
SENSITIVE_FILES = {".env", "id_rsa", "id_ed25519", "credentials.json", "service-account.json", "secrets.json"}
SENSITIVE_EXTENSIONS = (".p12", ".pfx", ".pem", ".keystore", ".kdbx", ".sqlite", ".sqlite3")

def git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    if p.returncode:
        raise ValueError("Git inspection failed")
    return p.stdout

def fingerprint(value):
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:10]

def categories(s):
    return {name for name, rx in PATTERNS.items() if rx.search(s)}

def path_categories(path):
    result = categories(path)
    name = Path(path).name.lower()
    if name in SENSITIVE_FILES or (name.startswith(".env.") and name not in {".env.example", ".env.sample", ".env.template"}):
        result.add("sensitive-file")
    if name.endswith(SENSITIVE_EXTENSIONS):
        result.add("sensitive-filetype")
    return result

def scan(root, base=None, metadata=None):
    root = root.resolve()
    head = git(root, "rev-parse", "HEAD").strip()
    refs = None
    if base and base != "0"*40:
        if not re.fullmatch(r"[a-fA-F0-9]{40}", base):
            raise ValueError("Invalid base")
        common = git(root, "merge-base", base, head).strip()
        names = [s for s in git(root, "diff", "--name-only", "--diff-filter=ACMR", "--no-ext-diff", common, head, "--").splitlines() if s]
        refs = (common, head)
    else:
        names = [s for s in git(root, "ls-files", "--cached").splitlines() if s]
    if any(s.startswith('"') for s in names):
        raise ValueError("Unreviewed encoded path")
    findings = set()
    for path in names:
        for c in path_categories(path):
            findings.add((fingerprint(path), c))
    if refs:
        diff = git(root, "diff", "--no-ext-diff", "--no-textconv", "--unified=0", *refs, "--")
        current = "changed-file"
        for line in diff.splitlines():
            if line.startswith("+++ b/"):
                current = line[6:]
            elif line.startswith(("Binary files ", "GIT binary patch")):
                findings.add((fingerprint(current), "binary-review-required"))
            elif line.startswith("+") and not line.startswith("+++"):
                for c in categories(line[1:]):
                    findings.add((fingerprint(current), c))
        authors = git(root, "log", "--format=%aN <%aE> | %cN <%cE>", f"{refs[0]}..{refs[1]}")
        for row in authors.splitlines():
            for c in categories(row):
                findings.add(("commit-metadata", c))
    else:
        for path in names:
            p = root / path
            if not p.is_file() or p.is_symlink():
                findings.add((fingerprint(path), "unsupported-file-review-required"))
                continue
            b = p.read_bytes()
            if b"\x00" in b or len(b) > 2_000_000:
                findings.add((fingerprint(path), "binary-or-large-review-required"))
                continue
            for c in categories(b.decode("utf-8", "replace")):
                findings.add((fingerprint(path), c))
    for value in metadata or []:
        for c in categories(value):
            findings.add(("public-metadata", c))
    return sorted(findings)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--base", default="")
    ap.add_argument("--from-event", action="store_true")
    opt = ap.parse_args()
    md = [os.getenv("PR_TITLE", ""), os.getenv("PR_BODY", "")] if opt.from_event else []
    try:
        flags = scan(opt.root, opt.base, md)
    except (OSError, UnicodeError, ValueError):
        print("SAFE STOP: privacy check incomplete", file=sys.stderr)
        return 2
    if flags:
        print(f"SAFE STOP: {len(flags)} privacy preflight finding(s)", file=sys.stderr)
        for code, category in flags[:25]:
            print(f"  {category} in {code}", file=sys.stderr)
        return 1
    print("PASS: basic privacy heuristics on changed files and metadata")
    print("Human review remains mandatory for names, context, imagery, history and publication rights")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
