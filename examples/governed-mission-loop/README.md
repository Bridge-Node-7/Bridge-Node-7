# Governed Mission Loop — offline reference candidate v0.1

**Status: experimental simulation; not an AI model, AGI, ASI, production runtime, security enforcement point, or deployed agent.**

This minimal standalone reference demonstrates one ingredient of a capability-compounding AI organization: converting a bounded mission proposal into a **reviewable, evidence-aware action preflight** with a role envelope, budget check, audit trace, and deterministic regression tests. It does not send messages, change files, connect to models, acquire credentials, read external websites, or call remote APIs.

## What problem it addresses

Multi-agent organizations can confuse a convincing model output with execution authority. This experiment keeps **action consequence class** separate from **autonomy permission**, and records exactly what a proposed agent would need before any real execution. This is preparation, not an authorization or a deployment.

## Try the synthetic mission

Requires Python 3.10+; standard library only.

```bash
python3 mission_loop.py examples/synthetic_public_mission.json > mission-report.json
python3 mission_loop.py --verify-audit mission-report.json
python3 -m unittest discover -s tests -v
```

Results for the example: read and draft are marked `SIMULATED_ONLY`; external sending is `HUMAN_REVIEW_REQUIRED`; transferring funds is `BLOCKED`. No operation actually happens.

## The action contract

- `A1`: declared read/check proposals; no real reads are performed.
- `A2`: draft/evaluation proposals; no agent is invoked.
- `A3`: proposed reversible internal change; needs human review.
- `A4`: proposed external or privileged action; needs separately authenticated human review every time.
- `A5`: prohibited agent execution (e.g., transfer money, contracts, deletion, self-authority changes).
- Unknown action, unknown role, missing references, or insufficient planning budget: **BLOCKED**.

Autonomy remains separate from this classification; **no action in this candidate acquires execution permission**. Role mappings are deliberately small and static; they are not claims of complete enterprise policy.

## Capability improvement and evaluation

`evaluate_golden()` runs precise policy-regression cases. `assess_skill_promotion()` rejects a candidate unless ten or more declared golden checks pass, critical-violation count is zero, declared task quality does not decline, and declared cost per accepted task improves. Even if the declared metrics pass, the result is **HUMAN_REVIEW_REQUIRED**, never deployment or automatic permission elevation.

The metrics are *inputs*, not measured benchmarks; a future integration must separately measure real user outcomes, maintain independent held-out evaluation cases, secure the evaluation dataset, and authenticate the human reviewer before any real action.

## What this proves / does not prove

Proves only deterministic local behavior on supplied JSON and the tests in this candidate. SHA-256 chaining detects changes to individual rows when the expected chain is retained; it neither authenticates the author nor prevents someone from rewriting the complete chain. Declared evidence status does not establish factual truth. Planning budget units are **not** actual API tokens or costs. The example does not demonstrate model intelligence, tool mediation, security isolation, customer impact, operational fitness, or AI self-improvement.

## Future integration boundary

An actual agent SDK could propose actions but must not directly execute them. A separately owned runtime must mediate **every tool call**, authenticate and bind explicit human approvals to action arguments, protect credentials and data, enforce quotas, isolate tenants, and emit protected audit events. Provider-side agents, prompts, and CI checks are not sufficient enforcement. Prefer existing agent SDKs, evaluation infrastructure, and policy/identity tools over rebuilding them.

The mission preflight may inform the human-owned decision and assurance architecture, but it must **not** become a substitute for domain-owned records, canonical intelligence, or evidence-graph reasoning. No cross-repository contracts are changed here.

Sources for design context: [OpenAI Agents SDK guardrails](https://openai.github.io/openai-agents-python/guardrails/), [OpenAI agent evaluations](https://developers.openai.com/api/docs/guides/agent-evals), [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework). These are references, not certifications or endorsements.
