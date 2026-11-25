# Proposal

## Why

PR #46 added the chain options of
[#45](https://github.com/gjed/roadsurfer-rally-map/issues/45) as plain dropdowns and
checkboxes, and #48 moved them into the `Chain options` chip's popover. The redesign
brief (part 3 of 4, `chain-options`) gives that control its own design: a popover on a
desktop and a sheet on a phone, with a segmented control, switches, a stepper and a
slider. On a phone the popover also covered the whole map, with no way to dismiss it
other than tapping a chip.

## What Changes

- Legs: a segmented control `2` · `3` · `2 or 3`.
- Between legs: a `Same day` switch, a `Rest days, up to N` stepper (0 to 7; `1 to N`
  with `Same day` off) and a `Next pick-up within` slider from the same station to
  ~250 km in steps of 25 km, which allows 75, 125, 175, 200 and 225 km as well.
- Whole trip: min days, max days and max km, and a `Round trip` switch.
- Footer: `Reset` and `Show N chains`, which counts live and closes the panel.
- The slider searches again 150 ms after it stops moving, typed numbers after 250 ms as
  before; meanwhile the count reads `Finding chains…`.
- Phone: the panel is a sheet from the bottom with a title and a close button, 44 px
  controls and a sticky footer. `Chains` opens it at once, as before; `Show N chains`,
  the close button, Escape and a tap above it dismiss it.
- The URL's `hop` takes any multiple of 25 from 0 to 250; the old values stay valid.

The search, the defaults, the URL parameters and the options' place among the filters
(`Clear all`, the chip) do not change. Out of scope: the phone bottom sheet with snap
points and the phone filter sheet (part 4).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the chain options' controls, the next pick-up distances and the
  phone sheet.
