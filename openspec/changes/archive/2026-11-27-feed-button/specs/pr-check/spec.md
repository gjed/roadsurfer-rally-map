# Delta for pr-check

## ADDED Requirements

### Requirement: App bar feed link check

The build check SHALL fail unless the generated page links `feeds/all.xml` from the app
bar with `class="fdbtn" href="feeds/all.xml"`, besides the link in `<head>`.

#### Scenario: Feed button removed

- **WHEN** a pull request removes the app bar feed link from the template
- **THEN** the build check fails
