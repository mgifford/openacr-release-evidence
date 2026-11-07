# Security and privacy

**Do not file publicly exploitable vulnerabilities or private Jira content.**
Before launch, configure GitHub private vulnerability reporting in repository
settings. Until configured, contact repository maintainers privately through a
secure agreed channel; do not transmit credentials in ordinary issue comments.

Threats include: prompt injection in issue text, malicious links, sensitive
tracker information leaking into public reports, compromised dependency versions,
API tokens committed in generated artifacts, and unbounded API/AI costs.

Controls: default offline operation, no browser-side secrets, strict URL schemes,
textContent-only rendering, bounded fetching and retries, minimized public JSON,
review gates for publishing, and secrets in CI environment configuration only.
The example workflow deliberately does **not** fetch live issues or auto-publish.

No SLA or security audit is claimed for this prototype. An independent security
review and real reporting channel are required before broader deployment.
