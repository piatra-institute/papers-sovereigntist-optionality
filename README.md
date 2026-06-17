# sovereigntist-optionality

**Sovereigntist Optionality: Capital Fractions and the Price of a Possible Future.** When a nationalist party becomes a credible route to power, "capital moves to the far right" hides its unit. This paper prices the situation as a real option over a population of firms indexed by state-dependence (the share of value the state allocates) and mobility (the share that can leave). A sovereigntist government arrives with probability `p`, reallocates a fraction of state-exposed value, and raises the country risk premium; each firm then hedges (buys a call on rents through access), exits (prices risk), or lobbies (voice). Solved over 60000 firms, the model finds a state-dependence threshold near 0.42 that sorts hedgers from exiters, so one rising probability sends mobile capital out and state-dependent capital toward the ministries at once: a bond sell-off and an access rush in the same week are one repricing seen from two fractions. The reach of the whole phenomenon is capped by rent-discretion, the parameter EU membership sets and the one the model is most sensitive to. Its sharpest result is negative: a cross-section of access holdings cannot tell option-buying from capture, since the two part only in the response to a change in `p`. Ships a runnable simulation (`simulation/`) whose `output/results.json` carries every modelled number.

## Build

```bash
uv run build.py          # -> paper/PAPER.pdf  (vendored canonical recipe)
```

Requires `pandoc` and `xelatex` on PATH. From the workspace you can also run
`papers build sovereigntist-optionality`.

Part of [piatra-papers](https://github.com/piatra-institute). See the workspace
docs for the research and writing pipelines.
