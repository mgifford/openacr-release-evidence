# Functional Performance Criteria mapping

The ACR includes a **Functional Performance Criteria (mapped)** summary based on
the CivicActions accessibility data reference:

- Source: <https://github.com/CivicActions/accessibility-data-reference>
- Data: `mapping-wcag-to-fpc.csv`
- Vendored: `config/fpc-wcag-mapping.csv`

The summary maps existing WCAG results to the nine Section 508 functional
performance categories. It is descriptive:

- it is not an independent functional-performance test;
- it does not populate OpenACR FPC values;
- the OpenACR FPC chapter remains Not Evaluated;
- a human must review any functional-performance claim.

## Disability labels in the criteria table

Each WCAG criterion in the ACR shows an **Affects:** line derived from the same
mapping, for example:

- Vision
- Limited vision
- Colour perception
- Hearing
- Limited hearing
- Speech
- Motor/manipulation
- Reach/strength
- Cognitive/learning

This is a short impact aid, not a severity ranking, not a complete disability
taxonomy and not a substitute for testing with disabled people. Criteria without a
mapping show `Affects: not mapped`.

## Deaf and hard of hearing

For Drupal Core, the native Web surface does not require hearing and has no
native audio/video playback. That means the deaf and hard-of-hearing community is
not broadly disadvantaged by Core's native Web surface.

The exception is authoring support: Drupal must help authors provide captions and
transcripts for the media they add. Known 1.2.2 authoring issues are potential
barriers, but they do not make the mapped **Without Hearing** result Partially
Supports. It remains **Not Evaluated** until reviewed evidence is recorded.

Contrib media players are separate products and need their own evaluation.

## 1.4.2 Audio Control

Drupal Core has no native audio playback or automatic audio feature to control.
1.4.2 is therefore Not Applicable for the declared Core scope, like the other
native media criteria. Contrib players are separate.

## Limits

- The mapping is based on WCAG 2.0 mappings and is applied to WCAG 2.2 results.
- It groups criteria; it does not simulate a person's functional experience.
- A mapped result is not a substitute for testing with disabled people.
- N/A claims still require factual product-scope review.
