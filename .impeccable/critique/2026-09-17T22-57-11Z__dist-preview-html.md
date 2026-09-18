---
target: dist/preview.html
total_score: 24
max_score: 32
na_heuristics: 7,10
p0_count: 2
p1_count: 2
target_identity: "file:/Users/jimbarnthouse/Documents/Claude/Projects/Hill Yard Sale Map/dist/preview.html"
target_fingerprint: "sha256:f27dcaaa48302030dfc486afa1f3c6f97fc2f55b7222a4beaf70f9d7ea35e924"
target_path: /Users/jimbarnthouse/Documents/Claude/Projects/Hill Yard Sale Map/dist/preview.html
timestamp: 2026-09-17T22-57-11Z
slug: dist-preview-html
---
Method: dual-agent (A: a7c100fb1a370c106 · B: a1e81498a4209a633)

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3/4 | "Happening now"/"Ended" pill and live tally work well; nothing missing at this scale |
| 2 | Match Between System & Real World | 4/4 | Real street names, verbatim payment strings, Directions hand-off to Google Maps |
| 3 | User Control and Freedom | 4/4 | Any house can become #1, filters reset cleanly, Escape closes popups |
| 4 | Consistency and Standards | 2/4 | Landmark markers visually compete with sale pins as if another category; detector confirms real text-occlusion between UI chrome and map labels |
| 5 | Error Prevention | 2/4 | Dense clusters are a mistap trap — no cluster-aware hit-target logic yet |
| 6 | Recognition Rather Than Recall | 4/4 | Numbers cross-referenced between map and list; selection highlighted in both |
| 7 | Flexibility and Efficiency | n/a | Operate-mode walking tool; no power-user path expected |
| 8 | Aesthetic and Minimalist Design | 2/4 | Strong type/color system undercut by unresolved pin collision and measured low-contrast/undersized-text findings |
| 9 | Error Recovery | 3/4 | Clear empty-filter state with recovery instruction |
| 10 | Help and Documentation | n/a | Self-explanatory for its mode; no help needed |
| **Total** | | **24/32** | **75% — Good, with a real P0** |

## Design Specificity Verdict

**LLM assessment (Assessment A):** Unmistakably authored for this event, not a generic map template — the palette is drawn from The Hill's actual brick/basil identity, copy is concrete ("Sat Sep 26, 8am-noon," verbatim payment quirks), and the route is a real solved walking loop with a stated legibility/distance tradeoff. A generic product would never bother GPS-surveying three houses or building a numbering model where any house can become #1 without breaking the map<->list cross-reference. This passes cleanly.

**Deterministic scan (Assessment B):** CLI `detect` on `build/template.html` returned exit 2 with 13 findings: 3 low-contrast pairs (worst is 1.2:1 text-on-background, need 4.5:1), 1 cramped-padding, 1 undersized-ui-text (10px "0.1 mi" under the 11px floor), and 8 gpt-thin-border-wide-shadow advisories (1px border + wide shadow, likely a handful of distinct card/pill classes rather than 8 unique elements). The live browser overlay independently caught 237 messages, dominated by every filter pill/tag/street label rendering at 10.5px (below an 11px floor) and 7 real text-occlusion instances: "WILSON AVE" 83% covered, "DAGGETT AVE" 67% covered, and pin numbers 12/13/37/39/42 41-83% covered by button.mbtn or span.bd. This is a mechanically-confirmed version of the handoff's own flagged concern (landmark labels overlapping pins) - it's broader than landmarks; it's street labels and pin numbers getting covered by UI chrome, not just by each other.

**Visual overlays:** No user-visible overlay tab was left open - Assessment B ran the detector, read console findings, and tore the live-server down before returning. The 237 console messages above are the full evidentiary record.

## Overall Impression

The bones are excellent - real product thinking, a defensible aesthetic rooted in the neighborhood, and engineering choices (the s.i/startAt numbering model, the honest binary payment invariant) a generic map tool would never make. But the single interaction the whole thing exists to support - matching a numbered pin to a numbered list entry - breaks exactly where the map is densest, and the detector confirms the breakage is worse and more widespread than the handoff's own framing suggested. The biggest opportunity is treating this as one root-cause problem (the dense core is simultaneously too small, too low-contrast, and too crowded) rather than three separate cosmetic patches.

## What's Working

1. The numbering model - identity fixed to s.i, printed number derived from startAt - lets anyone start anywhere without ever breaking the map<->list cross-reference.
2. The live pill and payment invariant show the model matches reality rather than just looking right.
3. Full dark-mode realization - separate token sets for explicit light/dark/system, good contrast in both modulo the specific flagged pairs.

## Priority Issues

**[P0] Dense pin collision at default/mid zoom (Daggett/Dempsey cluster).**
Why it matters: this is the literal core interaction. Detector confirms pin numbers 12/13/37/39/42 are 33-83% covered; pins 40/41/43 and 26/27 visibly touching with numbers hidden.
Fix: zoom-triggered cluster badges (expand/spiderfy past a threshold) rather than shrinking pins further (already tried, insufficient).
Suggested command: /impeccable layout

**[P0] Route line self-crossing with no direction cue in the dense core.**
Why it matters: the map's promise is "walk it in order" - self-intersecting line with no arrowhead breaks that promise exactly where it matters most.
Fix: periodic arrowheads/chevrons via marker-mid on the SVG path; consider rendering under pins at reduced opacity.
Suggested command: /impeccable layout

**[P1] Confirmed contrast and text-size floor failures, broader than the handoff's own concern.**
Why it matters: detector mechanically confirmed 3 low-contrast pairs (worst 1.2:1, need 4.5:1) and every filter pill/tag/street label at 10.5px (below 11px floor) - measured evidence directly compounding the handoff's own sunlight-legibility worry.
Fix: raise minimum rendered text size for pills/tags/street labels above 11px; fix the named low-contrast pairs, especially the 1.2:1 one.
Suggested command: /impeccable typeset

**[P1] Landmark and street labels get covered by UI chrome, not just by each other.**
Why it matters: detector shows "WILSON AVE" (83% covered) and "DAGGETT AVE" (67% covered) covered by button.mbtn (a map control), and pin numbers covered by span.bd - a general z-order problem, not just landmarks vs. pins.
Fix: extend the existing tricolore-bar collision logic to a general pass across all map-overlay elements (labels, controls, pin numbers).
Suggested command: /impeccable layout

**[P2] 13 filter chips scroll horizontally on mobile with no edge affordance.**
Why it matters: a chip cut off mid-word ("Vint...") with no fade hint that more exist; distracted mobile users may not realize the list continues.
Fix: subtle right-edge mask-image linear-gradient fade.
Suggested command: /impeccable polish

## Persona Red Flags

**Riley (Stress Tester):** hit targets already touching at collision zoom in the Daggett/Dempsey cluster - fast precise tapping isn't reliably possible there. Can tap "start here" on either flagged outlier (Magnolia/Sublette) with zero in-UI warning about the resulting spur-first loop.

**Casey (Distracted Mobile User, outdoors):** confirmed 10.5px pill/tag/street-label text and the 1.2:1-contrast pair are exactly what Casey needs to trust at a glance in bright sunlight - now a measured risk, not a hypothetical. Tricolore bar's tall/thin ratio (>10:1) at 375px reads as a rough first-impression, though not function-breaking.

**Jordan (First-Timer):** first fit-all view is dominated by the unreadable pin cluster at the visual center - the worst possible first impression for a tool asking to be trusted on a real walk.

## Minor Observations

- Sticky-map bottom-edge card clipping on mobile scroll: real but low-urgency, standard sticky behavior.
- Neighborhood Center is both a landmark marker and sale pin #59 at the same coordinate - small identity confusion layered on the label-occlusion issue; Jim's call per the handoff.
- 2227 Stephen Ct vs. Stephen Ave - worth a two-minute confirmation with Jim before the 26th.
- Popup item list scrolls internally at 132px max-height with no visible "more below" cue for multi-seller addresses.
- No console errors or warnings observed at any tested viewport width.

## Questions to Consider

1. If Daggett is the densest, most failure-prone block on the whole map, why is 5235 Daggett Ave the default start point?
2. Three "overlap in the dense core" issues (pins, route line, labels) plus two measured floor failures (contrast, text size) cluster in the same small area under the same root cause - one structural fix or five separate polish items?
3. Given 9 days to the event and a mechanically-confirmed P0 still open, is "polish" still the right framing, or is pin collision a functional blocker that outranks the rest of the punch list?
