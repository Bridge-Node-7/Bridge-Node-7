# Public Information Flow

Bridge Node 7 public repositories are publication surfaces, not mirrors of private working systems.

## Permanent rule

**Public surfaces receive standalone derivatives, not private context.**

A public artifact should be understandable and supportable from the evidence, attribution, limitations and rights information intentionally included with that artifact. It must not depend on access to a private repository, private branch, internal evidence locator, workspace path, chat record or hidden approval receipt.

The release path is:

```text
PRIVATE SOURCE
        |
        | private review + minimum-necessary transformation
        v
PUBLIC-SAFE CANDIDATE
        |
        | exact candidate + human authorization
        v
PUBLIC REPOSITORY / SITE
        |
        | repository-native checks + deployment
        v
PUBLIC READBACK
```

The private review receipt remains private.

## What public repositories must not expose by default

- links or raw-content URLs to nonpublic Bridge Node 7 repositories;
- private branch or source-history locators;
- local workspace or sandbox paths;
- ChatGPT conversation/project URLs used as internal working context;
- connector/file citation identifiers or other private retrieval handles;
- raw private notes, evidence IDs or internal deliberation required only to reconstruct how the derivative was produced.

Legitimate attribution to external public sources is preserved. Public GitHub links to the allowlisted public Bridge Node 7 estate are also allowed.

## What this gate does

The organization profile repository maintains a bounded public-estate ingress scan.

It verifies public default branches for:

- organization GitHub links that point outside the known public estate;
- raw-content links that point outside the known public estate;
- workspace/sandbox locators;
- ChatGPT conversation/project locators;
- connector-style private file handles.

A finding causes a fail-closed CI result for review.

## What this gate does not do

This is not proof that every public byte is harmless, every historical commit is clean, every vulnerability is absent, or every legal/scientific publication decision is correct.

Each public repository retains its own license, security, scientific, release and deployment controls. Human release authority remains separate from CI.

## Sustainable architecture

The public estate should not need to know the topology, names or contents of private repositories.

The scanner therefore works from a **public allowlist**: an organization GitHub link is permitted only when it targets a repository already known to be public. Anything else is treated as nonpublic or unknown and requires review.

That provides a durable control without publishing a private denylist.

**Transform, do not sync.  
Public allowlist, not private denylist.  
Minimum necessary disclosure.  
Independent release authority.**
