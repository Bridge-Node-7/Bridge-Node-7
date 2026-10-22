# Public privacy and publication boundary

## Purpose

Make public research reproducible without distributing personal identity, credentials, operational logs or confidential context. This policy applies to every public repository, website mirror, issue, pull request, commit and release.

## Default publication rule

Public content is limited to intentional company identity, approved public contact channels, independently releasable code, synthetic examples and properly attributed published research. Private matters, personal history, personal accounts, residential locations, personal credentials, financial/medical/family records, unapproved correspondence, unique source identifiers, unpublished proposals, contract terms and non-public client data are not public source material.

A proper noun is not automatically personal data: published researchers and organizations may be cited when accurate and necessary. Do not add personal associations, informal names, aliases or operational identity breadcrumbs solely for storytelling or demonstrations.

Use role identifiers such as "reviewer", "operator" and "organization maintainer", rather than personal accounts. Use generic fictional examples in tests. Avoid personal Git usernames, local home paths, personal emails, phone numbers, snapshots of desktop windows, real raw research notes and screenshots containing metadata.

## Release gates

1. Inventory all changed content: tracked files, filenames, added/modified lines, images/document metadata, PR body/title, issue comments, commits, tags, workflow logs, built site assets and releases.
2. Run the automated privacy preflight as well as existing code/secret scanning. CI failure is a stop sign, not a suggestion to disable the control.
3. Review every proper noun and source citation for necessity, lawful use and third-party rights.
4. Confirm commercial identity or published source references are intentional; remove personal contact information and local paths.
5. Confirm sanitized synthetic fixtures, technical facts, licensing and public release authority.
6. For a potential leak, do not reproduce the value in a public PR, issue, job log, report or alert. Record it in an approved restricted incident system using a generic reference.
7. Remove exposed credentials at the provider and rotate them. A commit deletion does not revoke a credential.
8. When previously published PII is discovered, distinguish current files from Git history, forks, caches, cloned checkouts, mirrors, Actions logs and release artifacts. Coordinate rewriting only with repository administrators, a backup and a force-with-lease plan; rewriting cannot retract third-party copies.
9. Recheck official deployed pages, repository metadata and public discoverability after remediation. Run regressions before merging.

## Enforcement and limitations

The privacy preflight catches selected email domains, local paths, phone-number formats, credential shapes and sensitive filenames. It does **not** determine which human proper nouns are sensitive, whether a business email is private, whether image/PDF EXIF contains identity, or whether a historical Git object has leaked data. Review of full commit history, PR/issue comments, branch protection, organization members, GitHub Actions permissions, secret scanning, old releases and hosting caches is a separate gate.

A workflow passing is not an OPSEC clearance. Require this workflow as a branch status check where administrative access permits. No publication should rely on a single automated detector.

## Decision rule

If scope, provenance, personal association, legal authorization or data ownership is unclear: **SAFE STOP / PRIVATE REVIEW**. Keep the public explanation generic and make the specific decision in a restricted record.
