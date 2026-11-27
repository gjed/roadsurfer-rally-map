## ADDED Requirements

### Requirement: App bar feed button

From 700 px wide the app bar SHALL have a 36 by 36 px RSS icon button between the scan
time and the `Display` button, which stays last. It SHALL link `feeds/all.xml` in a new
tab with the type `application/atom+xml`, match the `Display` button's border, radius and
surface in both themes, and have the accessible name `RSS feed` and a title that says it
carries every new rally, in the interface language. Below 700 px it SHALL NOT be shown.

#### Scenario: Desktop

- **WHEN** the page is opened 1440 px wide
- **THEN** the app bar ends with the scan time, a 36 px square RSS button and `Display`,
  and the button links `feeds/all.xml` in a new tab

#### Scenario: Tooltip in German

- **WHEN** the page is shown in German and the user points at the button
- **THEN** its name is `RSS-Feed` and its title is `Alle neuen Rallyes, für eine
  Feed-Reader-App.`

#### Scenario: No button on a phone

- **WHEN** the page is opened 390 px wide
- **THEN** the app bar has no feed button

### Requirement: Feed link in the Display sheet

Below 700 px the `Display` sheet SHALL end with a section after `Theme` holding an
`RSS feed` link to `feeds/all.xml` (new tab, type `application/atom+xml`) and the line
`Every new rally, for a feed reader app.` that the link names with `aria-describedby`.
From 700 px the section SHALL NOT be shown.

#### Scenario: Phone sheet

- **WHEN** the page is 390 px wide and the user opens `Display`
- **THEN** the last section of the sheet has the `RSS feed` link, 44 px tall, with its
  line below

#### Scenario: Desktop popover

- **WHEN** the page is 1440 px wide and the user opens `Display`
- **THEN** the popover opens under its button and has no feed section
