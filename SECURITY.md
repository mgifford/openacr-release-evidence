# Security and privacy

**Do not file publicly exploitable vulnerabilities or private tracker content.**
Before launch, configure GitHub private vulnerability reporting in repository
settings. Until configured, contact repository maintainers privately through a
secure agreed channel; do not transmit credentials in ordinary issue comments.

Threats include: prompt injection in issue text, malicious links, sensitive
tracker information leaking into public reports, compromised dependency versions,
API tokens committed in generated artifacts, raw CLI output published by mistake,
and unbounded API/AI costs.

Controls:

- Read-only Drupal.org/GitLab access; the CLI bridge has a command and flag
  allowlist and never calls mutating commands.
- Raw issue/CLI snapshots are written under `private-evidence/` with mode `0600`
  and are never overwritten. The directory is gitignored.
- The public collection, analysis and report contain normalized public data; they
  do not embed raw CLI payloads or secrets.
- Default offline operation, no browser-side secrets, strict HTTPS URL schemes,
  textContent-only explorer rendering, escaped static report rendering, bounded
  fetching and retries, and review gates for publishing.
- Git containment uses public refs; no token is required for the current reads.
- AI is off by default and is not used in the current report. If enabled, tokens
  stay server-side and model output remains untrusted.

The example workflow does not fetch live issues or auto-publish. Publication of
`reports/` to GitHub Pages is a human decision, not an automatic action.

No SLA or security audit is claimed for this prototype. An independent security
review and real reporting channel are required before broader deployment.
