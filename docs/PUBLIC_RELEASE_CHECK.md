# Bridge Node 7 | Public Release Scope

Official releases identify the material intended for public access: source code, documentation, reference data, generated artifacts, or browser-delivered assets.

A published artifact should have a clear source and revision, the notices required by its applicable terms, and a defined validation scope. Release checks also address unintended disclosure of credentials, confidential information, restricted content, and third-party material.

Passing tests, producing a build, or making a file publicly reachable does not by itself establish permission to publish it, source credibility, scientific validity, or operational readiness.

Each project retains its own release and rights requirements. See the public [IP and publication boundaries](../IP_POLICY.md) and the repository-specific license.

## Pull-request metadata boundary

Use short, neutral PR titles describing the change rather than identities, personal accounts, internal deliberations, unannounced relationships, unreleased terms or security findings. Exclude personal contact details, local filesystem paths, authentication material and links containing credentials. Descriptions and logs follow the same minimum-disclosure rule. Legitimate public scholarly attribution is not automatically prohibited.

The public profile checks its own PR title on creation and edits, and periodically inspects open PR titles in the selected public repositories. This is a bounded metadata review, not a guarantee against historic Git exposure, hidden credentials, source vulnerabilities or provider-side records. Private-repository titles and internal records must stay outside public CI artifacts and must be reviewed with separately authorized access. Merge and deployment authorization remain distinct human decisions.
