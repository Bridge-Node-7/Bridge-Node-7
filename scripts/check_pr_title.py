#!/usr/bin/env python3
"""Check public PR titles without echoing the title or disclosing private metadata."""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from urllib.request import Request, urlopen

REPOS = (
    "Bridge-Node-7", "ai-cyber-assurance",
    "frontier-decision-engine", "frontier-intelligence-workflows",
    "frontier-mission-assurance", "materials-to-mission",
    "pax-silica", "quantum-readiness-space-communications",
)
UNSAFE = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}", re.I),
    re.compile(r"(?:https?://|www\\.)", re.I),
    re.compile(r"(?:[A-Z]:[\\\\/](?:Users|Documents and Settings)[\\\\/]|/(?:Users|home)/[^/\\s]+)", re.I),
    re.compile(r"(?<![0-9])[2-9][0-9]{2}[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}(?![0-9])"),
    re.compile(r"\\b(?:founder-led|private draft|personal account|access token)\\b", re.I),
)

def acceptable(value):
    return (isinstance(value, str) and bool(value.strip()) and len(value) <= 120
            and not any(ord(c) < 32 for c in value)
            and not any(pattern.search(value) for pattern in UNSAFE))

def titles(repo):
    for page in range(1, 11):
        request = Request(
            f"https://api.github.com/repos/Bridge-Node-7/{repo}/pulls?state=open&per_page=100&page={page}",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "public-pr-metadata-review"},
        )
        with urlopen(request, timeout=15) as result:
            batch = json.load(result)
        if not isinstance(batch, list):
            raise ValueError("Unexpected metadata")
        for item in batch:
            yield item["number"], item.get("title")
        if len(batch) < 100:
            return
    raise ValueError("Pagination audit bound reached")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title-env")
    parser.add_argument("--audit-public", action="store_true")
    args = parser.parse_args()
    if not (args.title_env or args.audit_public):
        parser.error("Specify an audit")
    failed = []
    total = 0
    if args.title_env:
        total += 1
        if not acceptable(os.environ.get(args.title_env)):
            failed.append("current PR")
    if args.audit_public:
        try:
            for repo in REPOS:
                for number, title in titles(repo):
                    total += 1
                    if not acceptable(title):
                        failed.append(f"{repo}#{number}")
        except Exception:
            print("SAFE STOP: public metadata review incomplete", file=sys.stderr)
            return 2
    if failed:
        for ref in failed:
            print(f"SAFE STOP: title metadata policy violation for {ref}", file=sys.stderr)
        return 1
    print(f"PASS: checked {total} public PR title(s) without reading private repositories")
    return 0

if __name__ == "__main__":
    sys.exit(main())
