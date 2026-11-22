# Tasks

## 1. Design review

- [ ] 1.1 Review the fixture and real-data pages at 1280 px and 375 px against #27 and record the findings in design.md

## 2. Map page

- [ ] 2.1 Split the toolbar into a summary row and grouped filters; fold the filters behind a `Filters` button below 700 px
- [ ] 2.2 Highlight active filters and groups and count active groups on the `Filters` button
- [ ] 2.3 Add a collapsible map legend for line, weight and markers
- [ ] 2.4 Replace the inline-styled popup list with a styled trip table; add `rel="noopener"` to its links
- [ ] 2.5 Accessible names, visible focus, AA contrast, live counts, `aria-sort`, focus into the popup on keyboard row selection
- [ ] 2.6 Inline SVG favicon in the page head

## 3. Documentation

- [ ] 3.1 Update the README where it describes the toolbar

## 4. Validation

- [ ] 4.1 `make test`, the Python 3.8 tests and an offline `make map` from the fixture pass
- [ ] 4.2 Headless Chrome on a real-data page at 1280 px and 375 px: screenshots before and after, keyboard pass, axe-core contrast check, favicon without 404, filters, row count against `#count`, row selection and booking links
- [ ] 4.3 `make lint` and the global markdown config pass
- [ ] 4.4 `openspec validate --strict --all` passes
