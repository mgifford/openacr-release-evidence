# Report terminology

**Status: implemented terminology for the release reports, 2026-11-12.**

This page defines the words used in the generated reports. It is the reference
for [`REPORT-USABILITY-REVIEW.md`](REPORT-USABILITY-REVIEW.md) and
[`REPORT-INFORMATION-ARCHITECTURE.md`](REPORT-INFORMATION-ARCHITECTURE.md).

The reports do not certify accessibility. They collect public reports, describe
what is known about each report's relationship to an exact release, and say what
still needs checking.

## The two labels beside every issue

### Drupal.org status

Where the issue stands in Drupal.org's development workflow: Active, Needs
review, Needs work, RTBC, Patch (to be ported), Closed (fixed), Closed
(duplicate), and so on.

- It is **not** a severity grade.
- It is **not** a release finding.
- "Needs work" means people are still working on the issue. It does not mean the
  problem is confirmed in the release being reported on.
- "Closed (fixed)" means the issue was closed as fixed on Drupal.org. The
  release report still checks separately whether the fix is included in the
  exact release.

### Applies to this release?

What the evidence says about whether the reported problem affects this exact
software version. The machine-readable values stay in the JSON artifacts; the
report shows these plain-language labels.

| Report label | Machine value | Meaning |
| --- | --- | --- |
| Verified problem (reproduced in this release) | `confirmed-affected` | The problem was reproduced in this exact release. The automated pipeline does not emit this value. |
| Probably affects this release (not reproduced) | `likely-affected` | Reports or code evidence suggest the problem exists here, but nobody reproduced it. |
| Fix included in this release (not behaviourally verified) | `confirmed-fixed` | A matching fix commit is contained in the release tag **and** the issue is closed fixed. This proves code inclusion, not that the barrier is gone. |
| Not present in this release | `not-introduced` | The affected component or feature is absent from this release. This is a scope fact, not a fix. |
| Outside this report's scope | `not-in-scope` | The component is outside the components declared for this report. |
| Not yet determined | `unknown` | There is not enough information to decide whether the problem affects this release. |

"Not yet determined" does **not** mean accessible or inaccessible. It means the
question has not been answered for this release.

## Evidence words

| Term | Meaning in this project |
| --- | --- |
| Reported issue | Someone filed a possible accessibility problem on Drupal.org. This is a report, not proof that the problem exists in a release. |
| Issue status | Where the issue stands in Drupal.org's workflow. Separate from release applicability. |
| Source information | Issue details, comments, merge requests, commits and linked tests collected from public sources. |
| Release applicability | Whether the reported problem affects a particular software version. |
| Likely affected / probably affects this release | Available information suggests the problem exists in this version, but it was not reproduced. |
| Verified problem | The problem was reproduced in the specified version. |
| Fix included | A relevant code change is present in the specified release. |
| Verified fix | Testing confirms that the reported barrier is resolved in the specified version. The current pipeline never emits this. |
| Unknown / not yet determined | There is not enough information to decide whether the problem affects this version. |
| Conformance determination | A reviewed conclusion about whether a specific accessibility requirement is satisfied. The current pipeline never emits one. |

## Why "evidence" is not one thing

The word "evidence" covers several different strengths of information:

1. **A report.** Somebody says a barrier exists. This is a lead.
2. **A proposed change.** A merge request exists. This is a proposal, not a fix
   in a release.
3. **Code inclusion.** A commit is contained in a release tag. This proves the
   code is present, not that it works.
4. **A reproduction.** Somebody tested the barrier in the exact release. This is
   the strongest kind of evidence the project can record, and the current
   automated pipeline does not produce it.
5. **A conformance determination.** A reviewer has evaluated the requirement
   against the declared scope and recorded a result. This project does not make
   that decision.

The report keeps these separate rather than collapsing them into "evidence" or
an accessibility score.

## Scope words

| Scope | Meaning | What can be concluded |
| --- | --- | --- |
| Core distribution | Everything bundled with the Drupal Core release. | Which components shipped, whether an issue's component is present at all. |
| Default installation | What the standard profile installs and enables. | Which components a stock install uses by default. A component can be bundled but not installed. |
| Configured product | A declared site or downstream product with its own Core version, modules, themes and profile. | Only conclusions about that declared configuration, not every Drupal site. |

The current release reports use a declared assessment target. The target's
manifest records the configuration; the stock profile is reported separately in
the release details. See [`COMPONENT-HISTORY-INVESTIGATION.md`](COMPONENT-HISTORY-INVESTIGATION.md)
and `data/component-inventory/` for exact-release inventories.

## Conformance terms are not report labels

OpenACR/ACR terms such as Supports, Partially Supports, Does Not Support, Not
Applicable and Not Evaluated describe a conformance determination. They are not
synonyms for the issue labels above.

- An open issue does not automatically make a criterion "Partially Supports".
- An empty issue queue does not make a criterion "Supports".
- An issue tagged `wcag143` is a candidate relevance signal, not a conformance
  result.

The current report generator leaves non-`Not Applicable` adherence values unset
in the OpenACR draft and shows "Not Evaluated" in the ACR narrative. A reviewer
must record any conformance result. See
[`CONFORMANCE-POLICY.md`](CONFORMANCE-POLICY.md).

## Words the reports avoid

- **Score**, **grade**, **pass**, **fail**, **compliant**, **certified** for
  issue counts or issue states.
- **Fixed** for a closed issue or a removed component. The report says
  "no longer active", "fix included" or "not present in this release" and
  explains what was actually checked.
- **Unknown** without an explanation. Each row gives a reason and a next step.
