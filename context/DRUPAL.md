# Drupal Core — ACR and AI context

**Status: human-maintained scope guidance, not evidence.**

## Product

Drupal Core is a web content management system with a public front-end and an
authoring/administration interface. It is not a standalone electronic-document
product and does not ship a separate installed software application.

## Component treatment

| Component | Proposed treatment |
|---|---|
| Web | Partially Supports |
| Electronic Documents | Not Applicable |
| Software | Not Applicable |
| Authoring Tool | Partially Supports |

These are proposed component-level results for review. Every criterion remains
`Not Evaluated` until a named reviewer completes it. `Partially Supports` needs a
specific explanation; `Supports` also needs an explanation.

Use the ACR template:
[`../templates/drupal-acr-template.md`](../templates/drupal-acr-template.md).

## Authoring vs web

Treat the following as **authoring/account** surfaces:

- paths containing `/admin`;
- `/user` paths, including `/user/1`, `/user/login`, `/user/password` and
  `/user/register`;
- reproduction steps that require logging in, an administrator account or the
  authoring UI.

Everything else defaults to **web**. An authoring interface can also serve live
content; classify the surface where the barrier occurs and explain ambiguity.
Record the basis (`admin-path`, `user-path`, `login-step`, `default-web`).

## Issue references

- Use `drupal:<nid>` and the Drupal.org issue URL.
- State the tracker status and observation date.
- Active/review-relevant issues only: Active, Needs review, Needs work, RTBC,
  Patch. Fixed/closed/postponed issues are excluded.
- Say **“no longer active”**, not “fixed,” when an issue leaves the active list.
- Do not claim a reopen without evidence; a close/reopen cycle between snapshots
  may appear only as activity.
- Inventory records have no comments/MRs/commit analysis. Do not imply that they
  do.
- Do not turn issue counts or tags into per-criterion conformance results.

## Video scope

Drupal Core has no audio/video playback, live audio/video, or core video player.
For 1.2.1 Audio-only and Video-only, 1.2.3 Audio Description or Media
Alternative, 1.2.4 Captions (Live) and 1.2.5 Audio Description (Prerecorded),
use **N/A for Core** and point to the contrib Able Player or Video modules for
separate assessment. These are content/media concerns, not core CMS features.

## What kind of attestation this is

This is an **issue-queue accessibility attestation**, not a WCAG-EM evaluation,
not a periodic sample-based vendor ACR and not a certification. When summarizing:

- describe known reported barriers, not a complete census;
- do not claim that an untagged criterion is supported;
- do not imply independent manual or assistive-technology testing;
- explain that the evidence is the public Drupal issue queue and linked issues;
- keep the report's draft and human-review status.

## AI summary rules

- Use only the supplied facts; do not invent issues, numbers or fixes.
- Discuss only changed/new/no-longer-active issues.
- Do not assign component or criterion results.
- Do not use conformance labels as conclusions.
- Cite issue IDs and link to the evidence; do not quote raw comments.
- Mark the digest as a draft for human review.
- The ACR narrative and OpenACR YAML are the authoritative artifacts; the weekly
  summary never modifies them.

## References

- <https://www.section508.gov/test/>
- <https://ictbaseline.access-board.gov/>
- <https://www.section508.gov/buy/authoring-tools/>
- <https://www.access-board.gov/ict/#504-authoring-tools>
