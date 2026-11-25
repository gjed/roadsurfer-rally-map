# Spec Delta

## MODIFIED Requirements

### Requirement: Chain settings

In chain mode the page SHALL show a `Chain options` group, hidden in trip mode: legs
(`2`, `3`, `2 or 3`; default `2`), `Same day` (on) with 0 to 7 rest days (0), the next
pick-up within (same station, `~25`, `~50`, `~100`, `~150`, `~250 km`; same station),
the shortest and longest trip days and the max total km (empty, meaning any) and
`Round trip` (off). Every control SHALL update the count, the list and the map at once.

#### Scenario: Defaults

- **WHEN** the user enters chain mode
- **THEN** the controls read `2`, `Same day` checked, `0`, `same station`, empty, empty,
  empty and `Round trip` unchecked, and no group is marked as changed

#### Scenario: Three legs

- **WHEN** the user selects `2 or 3`
- **THEN** the chains of 3 legs are added to the chains of 2 legs

#### Scenario: Exactly three legs

- **WHEN** the user selects `3`
- **THEN** every chain listed has 3 legs

### Requirement: Chain options layout

The `Same day` checkbox and the rest days SHALL read as one sentence: `Same day or up to N rest days` when checked, `Same day 1 to N rest days` when not. The group SHALL be the
first group of the filter bar, in the DOM and so in the tab order, and on one row on a
desktop. A control that is not at its default SHALL be marked; the group itself SHALL NOT
be marked while everything is at its default.

#### Scenario: Unchecked

- **WHEN** the user unchecks `Same day` and selects 3 rest days
- **THEN** the options read `Same day 1 to 3 rest days`

#### Scenario: Tab order

- **WHEN** a keyboard user tabs into the filter bar in chain mode
- **THEN** the first control reached is `Legs`

### Requirement: Chain rest days

Leg N+1 SHALL start on the day leg N ends or up to the selected number of rest days
later, never earlier; with `Same day` unchecked it SHALL start 1 to that many days after
leg N ends. The rest days SHALL go up to 7. A hand-over at the same station SHALL read
`Same-day hand-over in <station>` or `N rest days in <station>`.

#### Scenario: No rest days

- **WHEN** `Same day` is checked and rest days are 0
- **THEN** every second leg starts on the day the first ends

#### Scenario: Rest days allowed

- **WHEN** the user allows up to 2 rest days
- **THEN** every chain from before is still found and chains with 1 or 2 rest days are
  added, each showing its rest days

#### Scenario: Not the same day

- **WHEN** the user unchecks `Same day` and sets 3 rest days
- **THEN** every hand-over of every chain listed is 1, 2 or 3 days long

#### Scenario: Same day unchecked with no rest days

- **WHEN** the user unchecks `Same day` while rest days are 0
- **THEN** rest days become 1 and 0 can not be selected until `Same day` is checked again

### Requirement: Chain connections

Leg N+1 SHALL start at the station where leg N ended or, with a next pick-up distance
selected, at another station within that many km of it, measured as the straight line ×
1.3 rounded to 10 km and shown with `~`. A station SHALL NOT be a pick-up twice in one
chain. A hand-over to another station SHALL read `Same day` or `N rest days`, then its
distance and both stations.

#### Scenario: Strictest settings

- **WHEN** rest days are 0, `Same day` is checked and the next pick-up is the same station
- **THEN** every chain's legs hand over at the same station on the same day

#### Scenario: Connection allowed

- **WHEN** the user allows a next pick-up within 50 km
- **THEN** every chain from before is still found and chains with a connection of up to
  50 km are added

#### Scenario: Widest connection

- **WHEN** the user selects `~250 km`
- **THEN** chains with a connection of up to 250 km are listed

#### Scenario: Connection shown

- **WHEN** a chain's second leg starts 40 km from where the first ended
- **THEN** its hand-over reads like `Same day · ~40 km from A to B`

## ADDED Requirements

### Requirement: Chain empty-state hints

When no chain matches, the page SHALL suggest relaxing at most two chain options, in this
order and only those not at their widest: `allow same-day changes`, `allow more rest days`, `allow a farther next pick-up`, `allow 3 legs`, `remove the trip length, km or round-trip limit`.

#### Scenario: Two hints

- **WHEN** no chain matches with `Same day` unchecked and 3 rest days
- **THEN** the empty state reads `No chains match. Try: allow same-day changes, allow more rest days, or reset the filters.`

### Requirement: Chain trip limits

The trip days SHALL limit the days from the first pick-up to the last return, the max
total km SHALL limit the km of the legs (connections not included), and an empty field
SHALL mean no limit. `Round trip` SHALL keep only chains whose last return station is
the first pick-up station or, with a next pick-up distance selected, within that
distance of it. A chain SHALL keep the best dates that satisfy the trip days.

#### Scenario: Trip days

- **WHEN** the user sets a minimum of 10 and a maximum of 12 trip days
- **THEN** every chain listed lasts 10 to 12 days

#### Scenario: Max km

- **WHEN** the user sets 1500 max total km
- **THEN** every chain listed has 1500 km or less driven

#### Scenario: Round trip

- **WHEN** the user checks `Round trip` with the same station as next pick-up
- **THEN** every chain listed ends at the station where it starts

### Requirement: Chain options as filters

A chain option that is not at its default SHALL count as one filter in `Filters (n)`
and show `Reset` while chain mode is on, and `Reset` SHALL restore every chain option to
its default. In trip mode the options SHALL NOT count.

#### Scenario: Changed option

- **WHEN** the user changes the legs to `3`
- **THEN** the toolbar reads `Filters (1)` and `Reset` shows

#### Scenario: Reset restores chain options

- **WHEN** the user presses `Reset` after changing several chain options
- **THEN** every chain option is back to its default and `Reset` hides itself

### Requirement: Chain options on phones

On a phone, turning `Chains` on SHALL open the filter panel, with `aria-expanded` true on
`Filters`, so that the chain options show without tapping `Filters`.

#### Scenario: Chains on at 375 px

- **WHEN** the user presses `Chains` on a 375 px wide screen
- **THEN** the chain options are visible at the top of the panel and `Filters` is expanded

#### Scenario: Chains off

- **WHEN** the user presses `Chains` again
- **THEN** the filter panel stays as it is

### Requirement: Chain search time

With the widest chain options on a scan of about 800 offers, finding the chains SHOULD take
well under a second on a desktop, and the default options SHALL take under 100 ms.

#### Scenario: Default options

- **WHEN** the user enters chain mode on a scan of about 800 offers
- **THEN** the chains appear without a noticeable delay
