# Design

## Decisions

- **Dark floors .85, ceiling .95.** Measured on the Esri Dark Gray land (`#3F3F41` at zoom
  5, `#414143` at 7, `#474749` to `#49494B` at 9 and beyond), a one-trip line is 3.6, 3.5
  and 3.1:1 at the lightest land; the previous .75 was 2.8:1 there. Two trips and more
  are 4.0:1 at the ceiling. Light keeps .8 and .95: 3.2:1 on the land, 4.1:1 at the
  ceiling.
- **Chain ramp.** The step is .02 (it was .05), so opacity keeps carrying the count up to
  about 8 chains in light and 6 in dark; beyond that the weight (`min(1 + chains * .2, 3)`,
  which reaches its cap at the legend's 10 chains) does. The floor stays: it is what keeps a single leg at 3:1.
- **Dense overview.** Checked on a generated network at the scale of a real scan (601
  offers, 34 stations, 170 routes: 812 chains, the first 200 drawn, 147 legs) at 1440×900
  in light and dark. It is busy but legible, with the busiest legs on top. The weight
  cap is lowered from 4 to 3 px, not the floor, so crossings show through.

## Accepted exceptions to the 3:1 criterion of #57

- A one-trip line on the sea of the Light Gray tiles (`#D0CFD4`) is 2.6:1. The light
  route colour is the brief's and is 3.4:1 on that sea even at full opacity, so no floor
  reaches 3:1; the land, where most of a line runs, passes.
- The chip and pill borders (`--field`) are 1.5:1 in light and 1.7:1 in dark, the brief's
  values. A chip or pill is named by its text, so its border is not what identifies it.
  Inputs, selects and the stepper, whose border is their edge, use `--ctl-line` (3.2:1 in
  dark).
