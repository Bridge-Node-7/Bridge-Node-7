"""Governed Mission Loop v0.1: dependency-free, offline policy simulation.

NO agent execution, credentials, remote APIs, external sends, or human approval verification.
This is a candidate reference for evaluating a proposed mission plan before execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

VERSION = "0.1.0-candidate"
ACTION_CLASSES = {
    # Action classes and autonomy are intentionally not the same dimension.
    "READ_PUBLIC_SOURCE": ("A1", {"research", "engineering", "assurance"}),
    "DRAFT_RESEARCH_BRIEF": ("A2", {"research", "chief_of_staff"}),
    "DRAFT_CODE_CHANGE": ("A2", {"engineering"}),
    "RUN_OFFLINE_EVAL": ("A2", {"evaluation"}),
    "CHECK_POLICY": ("A1", {"assurance"}),
    "DRAFT_OUTREACH": ("A2", {"gtm"}),
    "PREPARE_INTERNAL_CHANGE": ("A3", {"engineering", "chief_of_staff"}),
    "SEND_EXTERNAL_MESSAGE": ("A4", {"gtm", "chief_of_staff"}),
    "MODIFY_PERMISSIONS": ("A4", {"engineering"}),
    "TRANSFER_FUNDS": ("A5", set()),
    "SIGN_CONTRACT": ("A5", set()),
    "DELETE_RECORDS": ("A5", set()),
    "SELF_MODIFY_AUTHORITY": ("A5", set()),
}
OFFICE_BY_GOAL = {
    "research": "research",
    "invention": "research",
    "engineering": "engineering",
    "evaluation": "evaluation",
    "outreach": "gtm",
    "assurance": "assurance",
}
_VALID_SOURCE_STATES = {"VERIFIED", "REPORTED", "HYPOTHESIS", "SIMULATED", "UNKNOWN"}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def _text(value: Any, name: str, limit: int = 240) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{name} must be a nonblank string up to {limit} characters")
    return value.strip()


def _integer(value: Any, name: str, maximum: int = 10000) -> int:
    if type(value) is not int or not (0 <= value <= maximum):
        raise ValueError(f"{name} must be an integer between 0 and {maximum}")
    return value


def validate_mission(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != {"mission_id", "owner", "goal", "domain", "budget_units", "sources", "actions"}:
        raise ValueError("mission must contain exactly mission_id, owner, goal, domain, budget_units, sources, actions")
    _text(payload["mission_id"], "mission_id", 80)
    _text(payload["owner"], "owner", 80)
    _text(payload["goal"], "goal", 500)
    if payload["domain"] not in OFFICE_BY_GOAL:
        raise ValueError("unrecognized domain")
    _integer(payload["budget_units"], "budget_units")
    if not isinstance(payload["sources"], list) or len(payload["sources"]) > 100:
        raise ValueError("sources must be a list of up to 100 declarations")
    sources = set()
    for src in payload["sources"]:
        if not isinstance(src, dict) or set(src) != {"id", "state", "reference"}:
            raise ValueError("source declarations require id, state, reference")
        sid = _text(src["id"], "source id", 80)
        _text(src["reference"], "source reference", 500)
        if sid in sources or src["state"] not in _VALID_SOURCE_STATES:
            raise ValueError("duplicate source id or invalid evidence state")
        sources.add(sid)
    if not isinstance(payload["actions"], list) or not 1 <= len(payload["actions"]) <= 100:
        raise ValueError("actions must be a nonempty list of up to 100 proposals")
    ids = set()
    for action in payload["actions"]:
        if not isinstance(action, dict) or set(action) != {"id", "role", "kind", "target", "budget_units", "source_ids"}:
            raise ValueError("every action requires id, role, kind, target, budget_units, source_ids")
        aid = _text(action["id"], "action id", 80)
        _text(action["role"], "role", 60)
        _text(action["kind"], "kind", 80)
        _text(action["target"], "target", 200)
        _integer(action["budget_units"], "action budget_units")
        if aid in ids:
            raise ValueError("duplicate action id")
        ids.add(aid)
        if not isinstance(action["source_ids"], list) or len(action["source_ids"]) > 100 or not all(isinstance(s, str) for s in action["source_ids"]):
            raise ValueError("source_ids must be a list of string IDs")
    return payload


def assess_action(action: dict[str, Any], source_ids: set[str], remaining: int) -> dict[str, Any]:
    """Fail-closed preflight only. Never executes or authenticates an approval."""
    action_digest = digest({key: action[key] for key in ("id", "role", "kind", "target", "budget_units", "source_ids")})
    base = {"id": action["id"], "class": "UNKNOWN", "status": "BLOCKED", "reason": "unknown action", "action_sha256": action_digest}
    entry = ACTION_CLASSES.get(action["kind"])
    if not entry:
        return base
    level, roles = entry
    base["class"] = level
    if level == "A5":
        base["reason"] = "prohibited agent action"
    elif action["role"] not in roles:
        base["reason"] = "role outside the declared action envelope"
    elif action["budget_units"] > remaining:
        base["reason"] = "mission budget exceeded"
    elif len(set(action["source_ids"])) != len(action["source_ids"]) or not set(action["source_ids"]).issubset(source_ids):
        base["reason"] = "unrecognized or duplicate evidence reference"
    elif action["kind"] == "DRAFT_RESEARCH_BRIEF" and not action["source_ids"]:
        base["reason"] = "research brief requires declared evidence references"
    elif level in ("A3", "A4"):
        base["status"] = "HUMAN_REVIEW_REQUIRED"
        base["reason"] = "requires separately authenticated human authority; no execution performed"
    else:
        base["status"] = "SIMULATED_ONLY"
        base["reason"] = "in-scope proposal; no tool execution or factual verification"
    return base


def _audit_append(audit: list[dict[str, Any]], event: dict[str, Any]) -> None:
    previous = audit[-1]["sha256"] if audit else "0" * 64
    envelope = {"seq": len(audit), "previous_sha256": previous, "event": event}
    audit.append({**envelope, "sha256": digest(envelope)})


def verify_audit(events: Any) -> bool:
    if not isinstance(events, list):
        return False
    previous = "0" * 64
    for seq, row in enumerate(events):
        if not isinstance(row, dict) or set(row) != {"seq", "previous_sha256", "event", "sha256"}:
            return False
        envelope = {"seq": seq, "previous_sha256": previous, "event": row["event"]}
        if row["seq"] != seq or row["previous_sha256"] != previous or row["sha256"] != digest(envelope):
            return False
        previous = row["sha256"]
    return True


def run(mission: Any) -> dict[str, Any]:
    """Build a reviewable dry-run receipt. Does not instantiate language models."""
    m = validate_mission(mission)
    audit: list[dict[str, Any]] = []
    _audit_append(audit, {"event": "MISSION_RECEIVED", "mission_id": m["mission_id"], "mission_sha256": digest(m)})
    remaining = m["budget_units"]
    known_sources = {s["id"] for s in m["sources"]}
    evaluated = []
    for action in m["actions"]:
        check = assess_action(action, known_sources, remaining)
        # Units are a planning budget only. No tokens or API costs are incurred.
        if check["status"] in {"SIMULATED_ONLY", "HUMAN_REVIEW_REQUIRED"}:
            remaining -= action["budget_units"]
        evaluated.append(check)
        _audit_append(audit, {"event": "ACTION_PREFLIGHT", "check": check})
    result = {
        "schema": "bn7.governed-mission-loop.simulation/0.1",
        "version": VERSION,
        "execution_state": "SIMULATION",
        "mission_id": m["mission_id"],
        "owner": m["owner"],
        "assigned_office": OFFICE_BY_GOAL[m["domain"]],
        "source_states": {s["id"]: s["state"] for s in m["sources"]},
        "source_warning": "Evidence states and references are input declarations, not independent validation.",
        "remaining_planning_units": remaining,
        "actions": evaluated,
        "audit": audit,
        "audit_note": "Local SHA-256 chaining detects accidental edits; it does not authenticate authorship or prevent full-chain rewriting.",
        "human_authority": "All consequential execution, review, publication, and promotion remain external to this simulation.",
    }
    return result


def evaluate_golden(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Exact pass/fail regression against declared expected preflight statuses."""
    results = []
    for case in cases:
        actual = {a["id"]: a["status"] for a in run(case["mission"])["actions"]}
        expected = case["expected_statuses"]
        results.append({"case": case["name"], "passed": actual == expected, "actual": actual})
    return {"total": len(results), "passed": sum(x["passed"] for x in results), "cases": results,
            "limitation": "These tests assess deterministic policy routing only, not model quality or runtime enforcement."}


def assess_skill_promotion(candidate: dict[str, Any]) -> dict[str, Any]:
    """Recommendation-only skill evaluation; cannot authorize new autonomy."""
    required = {"golden_total", "golden_passed", "critical_violations", "baseline_cost_per_accepted", "candidate_cost_per_accepted", "baseline_quality", "candidate_quality"}
    if not isinstance(candidate, dict) or set(candidate) != required:
        raise ValueError("candidate must supply the seven exact evaluation metrics")
    for key in ("golden_total", "golden_passed", "critical_violations"):
        _integer(candidate[key], key, 100000)
    for key in ("baseline_cost_per_accepted", "candidate_cost_per_accepted", "baseline_quality", "candidate_quality"):
        v = candidate[key]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not (0 <= v < 1000000):
            raise ValueError("invalid metric: " + key)
    if candidate["baseline_quality"] > 1 or candidate["candidate_quality"] > 1:
        raise ValueError("quality values must be rates from 0 to 1")
    reasons = []
    if candidate["golden_total"] < 10 or candidate["golden_passed"] != candidate["golden_total"]:
        reasons.append("minimum ten golden tests must all pass")
    if candidate["critical_violations"] != 0:
        reasons.append("critical safety violations present")
    if candidate["candidate_quality"] < candidate["baseline_quality"]:
        reasons.append("quality regression")
    if candidate["candidate_cost_per_accepted"] >= candidate["baseline_cost_per_accepted"]:
        reasons.append("no cost improvement")
    return {"disposition": "REJECT_CANDIDATE" if reasons else "HUMAN_REVIEW_REQUIRED",
            "reasons": reasons,
            "note": "Input metrics are unverified declarations. No skill is deployed, no authority promoted, and no real-world improvement established."}


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline governed mission simulation (never executes actions)")
    parser.add_argument("mission", nargs="?", help="Path to public-safe synthetic mission JSON")
    parser.add_argument("--verify-audit", metavar="REPORT", help="Verify chain integrity for a saved report")
    parser.add_argument("--golden", metavar="CASES", help="Run golden policy checks from a JSON case array")
    args = parser.parse_args()
    try:
        if args.verify_audit:
            outcome = {"audit_chain_integrity": verify_audit(json.loads(Path(args.verify_audit).read_text(encoding="utf-8"))["audit"])}
            print(json.dumps(outcome, indent=2))
            return 0 if outcome["audit_chain_integrity"] else 1
        if args.golden:
            outcome = evaluate_golden(json.loads(Path(args.golden).read_text(encoding="utf-8")))
            print(json.dumps(outcome, indent=2))
            return 0 if outcome["passed"] == outcome["total"] else 1
        if not args.mission:
            parser.error("supply a mission file, --golden, or --verify-audit")
        print(json.dumps(run(json.loads(Path(args.mission).read_text(encoding="utf-8"))), indent=2, ensure_ascii=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f"SAFE STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
