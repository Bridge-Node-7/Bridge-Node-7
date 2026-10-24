"""BN7 Mission Synergy Compass: offline, public-safe handoff planner.

This is not a model, live orchestrator, policy engine or cross-repository API
adapter. It points to existing independently owned public tools without invoking
or modifying them. All inputs and outputs are synthetic and preparation-only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from mission_loop import digest, run, validate_mission

SCHEMA = "bn7.mission-synergy-compass.plan/0.1"
ALLOWED_HANDLING = "PUBLIC_SYNTHETIC"

# Curated official PUBLIC entry points; neither authenticated APIs nor
# evidence of deployed integration or verified results.
CAPABILITIES = {
    "source-review": {
        "owner": "frontier-intelligence-workflows",
        "title": "Inspect claims and source roots",
        "url": "https://github.com/Bridge-Node-7/frontier-intelligence-workflows",
        "requires": "A bounded question and declared source references",
        "produces": "Human-reviewed claim, provenance and uncertainty notes",
        "next_proof": "Independently check cited sources and declared provenance roots",
        "limits": "Structural checks cannot establish factual truth or independent corroboration",
    },
    "materials-review": {
        "owner": "materials-to-mission",
        "title": "Inspect materials and supplier dependencies",
        "url": "https://bridgenode7.com/materials-to-mission/",
        "requires": "Requirements, material context, and public-safe supporting evidence",
        "produces": "Evidence-scoped materials or qualification-gap assessment",
        "next_proof": "Obtain domain expert review and real qualification evidence",
        "limits": "Does not certify supply, product qualification, or mission readiness",
    },
    "cyber-review": {
        "owner": "ai-cyber-assurance",
        "title": "Prepare defensible cybersecurity assurance",
        "url": "https://github.com/Bridge-Node-7/ai-cyber-assurance",
        "requires": "Authorized review scope, security requirements, and relevant evidence",
        "produces": "Human-reviewable control, evidence-gap, and assurance notes",
        "next_proof": "Reproduce control testing in an authorized environment",
        "limits": "Not an incident diagnosis, certification, or permission to access systems",
    },
    "mission-assurance": {
        "owner": "frontier-mission-assurance",
        "title": "Reconsider mission dependencies when evidence changes",
        "url": "https://github.com/Bridge-Node-7/frontier-mission-assurance",
        "requires": "A specific technical decision, assumptions, dependencies, and evidence",
        "produces": "Decision-basis review identifying support and reassessment needs",
        "next_proof": "Review affected assumptions, original records, and domain tests",
        "limits": "A stale decision basis is not automatically a new scientific answer",
    },
    "decision-brief": {
        "owner": "frontier-decision-engine",
        "title": "Prepare an accountable decision",
        "url": "https://bridgenode7.com/frontier-decision-engine/",
        "requires": "A human decision question, relevant context, and explicit unknowns",
        "produces": "Local decision brief for a human to inspect and decide",
        "next_proof": "Human owner reviews the actual evidence and records the decision separately",
        "limits": "No automatic decision, source retrieval, factual proof, or outside action",
    },
}
ORDER = tuple(CAPABILITIES)


def _nonempty_string(value: Any, label: str, max_chars: int = 500) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_chars:
        raise ValueError(f"{label} must be a nonempty string up to {max_chars} characters")
    return value.strip()


def validate_request(request: Any) -> dict[str, Any]:
    keys = {"schema", "handling", "mission", "capabilities", "beneficiary", "success_observation"}
    if not isinstance(request, dict) or set(request) != keys:
        raise ValueError("synergy request has unknown or missing fields")
    if request["schema"] != SCHEMA:
        raise ValueError("unsupported synergy schema")
    if request["handling"] != ALLOWED_HANDLING:
        raise ValueError("SAFE STOP: only explicitly public-safe synthetic examples are supported")
    validate_mission(request["mission"])
    _nonempty_string(request["beneficiary"], "beneficiary", 160)
    _nonempty_string(request["success_observation"], "success_observation", 300)
    selected = request["capabilities"]
    if not isinstance(selected, list) or not 1 <= len(selected) <= len(CAPABILITIES):
        raise ValueError("capabilities must be a nonempty bounded list")
    if not all(isinstance(cap, str) and cap in CAPABILITIES for cap in selected):
        raise ValueError("unknown capability; routing fails closed")
    if len(set(selected)) != len(selected):
        raise ValueError("duplicate capability")
    return request


def plan(request: Any) -> dict[str, Any]:
    """Create an advisory routing plan, never execute tools or authorize releases."""
    r = validate_request(request)
    preflight = run(r["mission"])
    stages = []
    for cap in ORDER:
        if cap not in r["capabilities"]:
            continue
        stages.append({
            "step": len(stages) + 1, "capability": cap,
            **CAPABILITIES[cap], "status": "HUMAN_PREPARATION_ONLY",
            "owner_of_decision": r["mission"]["owner"],
        })
    blocked = [a["id"] for a in preflight["actions"] if a["status"] == "BLOCKED"]
    pending = [a["id"] for a in preflight["actions"] if a["status"] == "HUMAN_REVIEW_REQUIRED"]
    return {
        "schema": SCHEMA,
        "execution_state": "SIMULATION",
        "handling": ALLOWED_HANDLING,
        "mission_id": r["mission"]["mission_id"],
        "mission_sha256": digest(r["mission"]),
        "request_sha256": digest(r),
        "accountable_human": r["mission"]["owner"],
        "beneficiary": r["beneficiary"],
        "proposed_success_observation": r["success_observation"],
        "stages": stages,
        "action_preflight": [
            {key: a[key] for key in ("id", "class", "status", "reason", "action_sha256")}
            for a in preflight["actions"]
        ],
        "blocked_proposals": blocked,
        "human_review_proposals": pending,
        "declared_uncertain_source_ids": [
            sid for sid, state in preflight["source_states"].items() if state != "VERIFIED"
        ],
        "readiness": "SAFE_STOP" if blocked else "HUMAN_PREPARATION_ONLY",
        "release_authorized": False,
        "external_execution_authorized": False,
        "limitations": [
            "Public references are standalone entry points, not compatible machine interfaces.",
            "No external repository was accessed, modified, or validated by this plan.",
            "Source states are declarations, not corroborated evidence or factual verification.",
            "Synthetic/public-safe handling is asserted by the submitter, not independently confirmed.",
            "No rights, authenticity, approval, runtime controls, or production safety are established.",
            "A safe route is not an automatic decision, customer result, or proof of intelligence gains.",
        ],
    }


def as_markdown(result: dict[str, Any]) -> str:
    """Readable local output. Not a verified or approved publication artifact."""
    lines = [
        "# Mission Synergy Compass — proposed route (synthetic)", "",
        f"Mission: {result['mission_id']}",
        f"Human owner: {result['accountable_human']}",
        f"Who benefits: {result['beneficiary']}",
        f"Desired observation: {result['proposed_success_observation']}",
        f"Disposition: {result['readiness']}", "",
        "## Existing tool handoffs", "",
    ]
    for stage in result["stages"]:
        lines += [
            f"### {stage['step']}. {stage['title']}",
            f"Official entry: {stage['url']}",
            f"Input: {stage['requires']}",
            f"Output: {stage['produces']}",
            f"Next proof: {stage['next_proof']}",
            f"Limit: {stage['limits']}", "",
        ]
    lines += ["## Action preflight", ""]
    for a in result["action_preflight"]:
        lines.append(f"- {a['id']}: {a['status']} ({a['reason']})")
    lines += [
        "", "## Uncertainties and release boundary", "",
        "All handoffs remain advisory. No work or execution occurred.",
        "No automatic authority, canonical admission, public release, or publication is granted.",
        "Declared uncertain evidence: " + (
            ", ".join(result["declared_uncertain_source_ids"])
            or "none declared; independently verify source truth"
        ), "", "Source request SHA-256: " + result["request_sha256"],
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline public-safe mission handoff planner")
    parser.add_argument("request", type=Path)
    parser.add_argument("--markdown", action="store_true", help="Print readable advisory handoffs")
    args = parser.parse_args()
    try:
        report = plan(json.loads(args.request.read_text(encoding="utf-8")))
        print(as_markdown(report) if args.markdown else json.dumps(report, indent=2, ensure_ascii=False))
        return 3 if report["readiness"] == "SAFE_STOP" else 0
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print(f"SAFE STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
