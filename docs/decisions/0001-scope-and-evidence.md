# ADR 0001: Separate release applicability from tracker status

Status: Accepted for prototype, subject to community review
Date: 2026-11-07

## Context

Drupal issues may describe development branches and fixes not present in
supported releases. Drupal CMS and LocalGov Drupal include Drupal Core but have
different installed packages and configuration.

## Decision

Store issue status independently from target-scoped applicability. Default to
`unknown`, permit explicit evidence overrides, and require evidence URLs and
rationale. Never derive conformance status from issue status, patch presence or
issue counts. Use exact target manifests when available. Human review and release
verification are separate steps.

## Consequences

The early prototype cannot generate a final ACR and many records will be
`unknown`. This is an intended safety feature, not a reason to invent certainty.
