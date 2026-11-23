# Spec Delta

## ADDED Requirements

### Requirement: Chains from the published data

The published page SHALL compute rally chains in the browser from the offers it
embeds. Neither `scan.yml` nor `release.yml` SHALL send an additional request, run an
additional step or store additional data for chains, and a page rendered from a data
file written by an earlier scan SHALL offer chains too.

#### Scenario: Release from an older artifact

- **WHEN** `release.yml` renders the page from an `offers` artifact written before
  chains existed
- **THEN** the deployed page offers chains and the release job sends no request to
  roadsurfer or to a routing server
