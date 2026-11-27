## Decisions

- **Icon only, in the bar.** A 36 px square matches the `Display` button's height,
  border (`--field`), radius and surface, so the bar keeps one rhythm. The icon is in
  `--ink`, not `--accent`: the feed is a secondary action and must not be louder than
  `Display`. The hover colour is set on the link so that the global `a:hover` accent
  colour does not win. Focus uses the global `:focus-visible`; there is no pressed state.
- **Accessible name and tooltip.** `aria-label` reuses `fav.feed` (`RSS feed`); the
  `title` is the new `feed.all.tip` ("Every new rally, for a feed reader app."). The
  static i18n loop already fills `data-t-aria-label` and `data-t-title`, so no script
  changes.
- **Markup.** The new link and the unchanged `.dispw` sit in one `.abtn` flex span (8 px
  gap) inside `.abend`, so the 16 px gap to the scan time stays. `placePop` measures
  `chip.parentNode`, which is still `.dispw`, so the Display popover opens in place.
  Order: scan time, feed, `Display` last.
- **Phones (below 700 px).** The square is hidden and the `Display` sheet gets a last
  `.dsec.dfeed` section after Theme: the `.feed` link (44 px tall, aligned with the other
  rows) and `feed.all.tip` as its description (`aria-describedby`). Tablets (700 to
  1099 px) keep the square. The section is `display: none` outside the phone query, so
  the desktop popover does not change.
- **Strings.** `fav.feed` is reused; `feed.all.tip` is new, in all seven catalogs
  (a new `feed.` namespace, not `fav.`, because it is not about favourites). The catalog
  test covers it in every language.
- **Cost.** The desktop app bar wraps 44 px earlier (36 px button and an 8 px gap), for
  example from 1117 to 1161 px in English and from 1299 to 1343 px in Portuguese on the
  fixture with a scan time. Accepted.
- **Check.** The PR check's page check and a unit test require
  `class="fdbtn" href="feeds/all.xml"` in the app bar, in step with the existing check of
  the `<head>` link.

## Rejected alternatives

- A visible label on a desktop: about 115 px more width and louder than `Display`.
- A label above about 1500 px only: one more breakpoint for little gain.
- An accent or orange icon: competes with the primary controls.
- Keeping the icon in the phone bar: the title wraps at 412 px even in English.
- Putting the link in the Filters sheet: the feed is not a filter.
- A new menu, a copy-URL button or a per-station feed list: more UI than the issue asks.
- JavaScript that moves one element on resize: two CSS rules do the same without a
  script.
