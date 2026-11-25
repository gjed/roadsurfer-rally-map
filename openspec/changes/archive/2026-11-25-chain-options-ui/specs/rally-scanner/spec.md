# Delta for rally-scanner

## MODIFIED Requirements

### Requirement: Chain settings

In chain mode a `Chain options` chip SHALL open a panel with: legs (`2`, `3`, `2 or 3`;
default `2`), a `Same day` switch (on), 0 to 7 rest days (0), a `Next pick-up within`
slider from the same station to ~250 km in steps of 25 km (same station), min days, max
days and max km (empty: any) and a `Round trip` switch (off). Every control SHALL update
the results; typed numbers after 250 ms and the slider after 150 ms, with `Finding chains…` in the count meanwhile.

#### Scenario: Defaults

- **WHEN** the user enters chain mode
- **THEN** the controls read `2`, `Same day` on, `0`, `same station`, empty, empty,
  empty and `Round trip` off, and the chip is not marked as changed

#### Scenario: Three legs

- **WHEN** the user selects `2 or 3`
- **THEN** the chains of 3 legs are added to the chains of 2 legs

#### Scenario: Exactly three legs

- **WHEN** the user selects `3`
- **THEN** every chain listed has 3 legs

#### Scenario: Moving the slider

- **WHEN** the user drags the next pick-up slider to `~150 km`
- **THEN** the count reads `Finding chains…` until the slider rests, then the chains
  with a connection of up to 150 km

### Requirement: Chain options panel

The panel SHALL group the options under `Legs`, `Between legs` and `Whole trip`. The
rest days stepper SHALL read `Rest days, up to N` while `Same day` is on and `Rest days, 1 to N` while it is off. Legs buttons SHALL carry `aria-pressed`, switches
`role="switch"`. The panel SHALL end with `Reset` (the chain options only) and `Show N chains`, which counts live and closes it. The chip SHALL be marked exactly while an
option is not at its default.

#### Scenario: Unchecked

- **WHEN** the user turns `Same day` off and sets 3 rest days
- **THEN** the stepper reads `Rest days, 1 to` 3 and its `−` stops at 1

#### Scenario: Tab order

- **WHEN** a keyboard user opens the `Chain options` panel
- **THEN** focus is on `Legs`, the first control, and Tab stays inside the panel

#### Scenario: Panel reset

- **WHEN** the user changes the legs and presses the panel's `Reset`
- **THEN** every chain option is back to its default and the other filters are kept

#### Scenario: Show the chains

- **WHEN** the user presses `Show 2,192 chains`
- **THEN** the panel closes and focus returns to the `Chain options` chip

### Requirement: Chain options on phones

Below 700 px the `Chain options` panel SHALL be a sheet from the bottom of the screen
with the title `Chain options`, a close button, controls at least 44 px tall and a
footer that stays in view. Turning `Chains` on SHALL open it, with `aria-expanded` true
on its chip. `Show N chains`, the close button, Escape and a tap above the sheet SHALL
close it.

#### Scenario: Chains on at 375 px

- **WHEN** the user presses `Chains` on a 375 px wide screen
- **THEN** the chain options sheet is open and its chip is expanded

#### Scenario: Chains off

- **WHEN** the user presses `Single rallies`
- **THEN** the chain options sheet closes and its chip is hidden

#### Scenario: Back to the map

- **WHEN** the user presses `Show N chains` in the sheet
- **THEN** the sheet closes and the map and its lines can be tapped

### Requirement: Chain connections

Leg N+1 SHALL start at the station where leg N ended or, with a next pick-up distance
selected, at another station within that many km of it, measured as the straight line ×
1.3 rounded to 10 km and shown with `~`; the distance, and the URL's `hop`, SHALL be a
multiple of 25 km up to 250. A station SHALL NOT be a pick-up twice in a chain. A hand-over to another station SHALL read `Hop ~N km <A> → <B> on your own`, then `same day` or `N rest days`, and be drawn with a dotted rule.

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
- **THEN** its hand-over reads like `Hop ~40 km A → B on your own · same day`

#### Scenario: A step between the old values

- **WHEN** the user opens a link with `hop=75`
- **THEN** the slider reads `~75 km` and chains with a connection of up to 75 km are
  listed; `hop=80` is ignored
