# Execution Authority

Bridge Node 7 operations use explicit execution states so review, simulation, repository work, releases, and production changes are never conflated.

## Default

If an instruction does not explicitly authorize mutation, the operating state is:

```text
READ_ONLY
```

Review, V&V, architecture analysis, status checks, simulation, and recommendations do not by themselves authorize writes.

## Execution states

### READ_ONLY

Allowed:

- inspect repositories, files, commits, branches, pull requests, issues, releases, workflows, and public surfaces;
- compare state;
- produce analysis, receipts, or proposed diffs outside the authoritative system.

Not allowed:

- create or modify repository state;
- trigger releases;
- change production.

### SIMULATION

Allowed:

- model exact proposed branches, files, pull requests, tests, gates, rollback steps, and expected effects.

Not allowed:

- perform the simulated mutation.

### CANDIDATE_BRANCH_ONLY

Allowed:

- create a bounded candidate branch;
- make only the explicitly scoped changes on that branch;
- run or observe candidate validation.

Not allowed:

- merge;
- release;
- deploy.

### PR_ALLOWED

Allowed:

- open a pull request for the scoped candidate;
- update that pull request only within the declared scope;
- observe CI and review.

Not allowed:

- merge unless separately authorized or the execution instruction explicitly includes autonomous merge after all declared gates pass.

### MERGE_ALLOWED

Allowed:

- merge the reviewed pull request only after declared checks pass and the expected head SHA still matches.

Not allowed:

- infer release or production authorization from merge authorization.

### RELEASE_ALLOWED

Allowed:

- invoke the repository's documented release path after release-specific gates pass.

Not allowed:

- broaden release scope or production scope beyond the declared artifact.

### PRODUCTION_ALLOWED

Allowed:

- deploy the explicitly named production surface using the reviewed release path;
- verify production parity after deployment.

This is the highest authority state and must never be inferred from lower states.

## Website and production rule

Repository work does **not** imply authorization to modify BridgeNode7.com, GitHub Pages, or any production deployment.

A website or production change requires its own explicit scope, reviewed diff, validation plan, and production authorization.

## Authority preservation

Automation may prepare evidence, validate structure, create bounded candidate changes, and execute pre-authorized mechanical steps.

Automation does not become the accountable owner of:

- scientific conclusions;
- mission qualification;
- independent V&V declarations;
- risk acceptance;
- security authorization;
- investment decisions;
- consequential human decisions.

## Fail-closed conditions

Stop before further mutation if any of the following occurs:

- the base or expected head moved unexpectedly;
- a contract digest changes outside scope;
- a private/public handling boundary changes;
- a candidate exposes protected material;
- a test passes for a reason outside its declared semantics;
- a release includes files outside the approved allowlist;
- a machine result is being promoted into human authority;
- production scope would be broader than explicitly authorized.

## Decision receipt

Every substantial execution should be able to state:

- current execution state;
- allowed repositories / systems;
- prohibited surfaces;
- exact base identity;
- intended files / behavior;
- validation gates;
- merge / release / production authority;
- rollback or safe-stop condition.

This makes execution authority inspectable in the same way Bridge Node 7 makes evidence and decision authority inspectable.
