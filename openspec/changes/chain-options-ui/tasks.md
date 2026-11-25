# Tasks

## 1. Controls

- [x] 1.1 Legs segmented control setting the hidden `cn`
- [x] 1.2 `Same day` and `Round trip` switches (`role="switch"` checkboxes)
- [x] 1.3 Rest days stepper on `cg`, 0 to 7, 1 to 7 with `Same day` off
- [x] 1.4 Next pick-up slider on `ck`, 0 to 250 km in steps of 25, with its label
- [x] 1.5 Whole trip: min days, max days, max km
- [x] 1.6 Footer `Reset` and live `Show N chains`

## 2. Behaviour

- [x] 2.1 Slider pause 150 ms, typed numbers 250 ms, `Finding chains…` meanwhile
- [x] 2.2 URL `hop` accepts any multiple of 25 up to 250
- [x] 2.3 Phone sheet: title, close button, 44 px controls, sticky footer; opened by `Chains`

## 3. Documentation and validation

- [x] 3.1 README "Chains"
- [x] 3.2 `make lint test map`, `openspec validate chain-options-ui --strict`
- [x] 3.3 Browser check at 1440×900 and 390×844 with the scan, the fixture and an empty scan
