# Public Release Check | Quiet by Default

**Scope:** only a change that becomes accessible outside its authorized private boundary. Public GitHub commits, rendered public documentation, website files, browser-delivered scripts, downloadable artifacts, and deliberately shared outputs are all disclosures.

## One question

Will this change intentionally reveal previously private capability, material invention, confidential or customer content, credentials, third-party material, or a material rights change?

- **No:** normal CI, code review, and release process. No extra IP ceremony.
- **Yes or uncertain:** hold only the affected public disclosure. Identify the material, relevant rights/permissions, owner, intended destination, and necessary approval before publishing.
- **Confirmed credential or restricted/customer-data exposure:** stop publication and use the appropriate security/incident process.

**Only record an exception receipt when a boundary is triggered.** A sufficient record identifies the asset/revision, classification, decision owner, supporting rights evidence, approved public artifact, and conditions for reassessment.

## Preserve engineering and evidence boundaries

- A green build or automated scan never determines authorship, trade-secret status, patentability, legal compliance, or public-release authority.
- If JavaScript is delivered to a browser, treat it as publicly inspectable even if it is built from a private repository.
- Do not use general governance text to alter or contradict repository-specific licenses.
- Flag actual accidental development residue and confidential leaks; preserve legitimate technical and security terminology.
- Preserve production while a candidate's product release gates remain open.

**Working principle:** silent normal flow, contextual human review for uncertainty, stop only proven unacceptable publication risks.
