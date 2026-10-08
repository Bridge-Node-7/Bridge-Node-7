# Bridge Node 7 | Publication and IP Boundaries

The goal is useful public reference work and durable proprietary advantage, with minimal day-to-day friction.

## Four publication classifications

| Classification | Working meaning | Publication action |
| --- | --- | --- |
| Public commons | Deliberately reusable materials where a repository-specific open license grants those rights | Honor the applicable local license and attribution conditions |
| Controlled public | Publicly inspectable materials with rights reserved or an expressly bounded evaluation posture | Confirm the governing local rights terms before reuse or disclosure |
| Proprietary core | Material intentionally handled within authorized private access and confidentiality boundaries | Do not disclose merely because a technical export is possible |
| Strategic invention | Potential novel mechanisms whose patent, trade-secret, or publication treatment has not been settled | Obtain an appropriate authorized invention/publication decision before disclosure |

These are internal handling labels, **not licenses, registrations, patents, certifications, or findings of trade-secret status**. An actual asset's treatment must be supported by the applicable rights and facts.

## Lightweight publication trigger

Before a newly public change, ask whether it reveals any of:

1. A materially novel mechanism or previously private capability.
2. Customer, confidential, restricted, or credential information.
3. Third-party material or a new licensing/rights obligation.
4. A change in the terms or scope of public licensing.
5. A public browser asset that was assumed to be private merely because its source repository is private.

If **no**, continue through ordinary engineering and release controls. If **yes or uncertain**, hold the affected publication, classify the specific material, and obtain a scoped owner review. Engineering success is not publication authorization.

## Rights and evidence

- Preserve existing MIT, Apache, and other licenses as granted. Do not graft incompatible anti-AI exceptions onto open-source rights.
- Publicly served JavaScript, HTML, CSS, source maps, and assets are inspectable regardless of repository visibility. Do not ship genuine secrets, private customer context, credentials, or proprietary-only algorithms in browser assets.
- Retain source and release identity, artifact checksums where applicable, material publication decisions, and any third-party use permissions.
- Maintain material ownership, chain-of-title, invention, disclosure, trade-secret, and incident evidence in authorized private systems. A registry alone does not establish rights.
- Do not assert scraping, infringement, registration, or ownership without sufficient evidence and appropriate review.

For this profile, [LICENSE](LICENSE) controls its original contents. Linked repositories each keep their own rights and source-of-truth.

This guidance is not legal advice and does not create new rights or revoke previously granted rights.
