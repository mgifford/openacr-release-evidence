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

The CI workflow does not fetch live issues or auto-publish. The Pages workflow
deploys only an explicit allowlist: a landing page and each report's HTML, CSS,
evidence JSON and summary. It rejects private-evidence paths, non-allowlisted
JSON (including raw collection/analysis files) and HTML containing client-side
scripts. Configure required reviewers on the `github-pages` environment if a
deployment should wait for a second approval. Publication remains a human
decision, not an automatic consequence of running the collector.

No SLA or security audit is claimed for this prototype. An independent security
review and real reporting channel are required before broader deployment.
