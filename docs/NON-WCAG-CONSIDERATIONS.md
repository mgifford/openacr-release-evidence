# Beyond WCAG: non-WCAG accessibility considerations

WCAG is the conformance baseline, not the whole of accessibility. The ACR therefore
ends with a separate **Beyond WCAG** box for issues that can create real barriers
without a clean WCAG 2.2 AA success criterion.

These are review prompts, not findings. They do not use Supports, Partially
Supports or Does Not Support and are not part of OpenACR.

## Current topics

- **EN 301 549 user preferences** — respect font size, contrast, colours, spacing
  and motion preferences; do not override user-agent or user choices.
- **Visually induced motion sickness** — parallax, large transitions, zooming and
  camera-like movement. WCAG 2.3.3 Animation from Interactions is Level AAA and
  does not cover every motion source at AA.
- **Reduced-motion preference** — honour `prefers-reduced-motion`.
- **Forced-colors/high-contrast mode** — keep controls, focus and status
  information perceivable.

Each item records:

- why it matters;
- evidence still to collect;
- `not-evaluated` / `unreviewed` status;
- a Drupal issue search link for follow-up.

## How to use it

These are not procurement conformance statements. If a topic becomes a finding,
record it with a target, source, evidence and reviewer, and decide whether it
belongs to a separate EN 301 549 or functional-performance assessment.

Contrib media players, themes and user-agent behavior are separate products and
must be evaluated in their own scope.
