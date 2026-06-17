# simulation

A real-options model of capital fractions facing a credible sovereigntist route to power.

```bash
uv run run_all.py     # -> output/results.json + output/figures/{crossing,identification}.png
```

## The model

A firm of value 1 splits into a state-discretionary share `s` (contracts, permits,
subsidies, regulated prices) and a market share `1 - s`; it can move a fraction `m`
of itself abroad. A sovereigntist government arrives with probability `p`, reallocates
a fraction `delta` of the state-exposed value, and raises the country risk premium by
`rho`. Each firm picks the maximum of four priced options:

- **hedge**  `H = p*delta*s*kappa - a*(1 - phi*(1-p))` — a call on reallocated rents bought with access premium `a`, salvage `phi` if the regime does not arrive.
- **exit**   `X = m*(p*rho*(1-s) - k)` — pull mobile value out of a repriced exposure.
- **voice**  `V = eta*p*rho*(1-s) - cv` — lobby for stability (the immobile, market-exposed corner).
- **stay**   `0`.

`H` rises in `s`, `X` falls in `s`, so they cross once at a state-dependence threshold
`s*(p, m)`. Above it firms hedge; below it they exit.

## Analyses (in `analyses.py`, written to `output/results.json`)

- **threshold** — `s*(p)` for three mobility levels; the two-firm illustration (a state-dependent contractor hedges, a mobile fund exits).
- **path** — population strategy shares as `p` rises; the population splits into hedge/exit/voice.
- **regimes** — three parameter triples standing for rising-semiperiphery, consolidated, and mainstreamed stages; separated by the access value at stake.
- **identification** — optionality vs capture: the reversibility of a hedging cohort when `p` recedes, and the value the cohort retains. The cross-section cannot tell the two apart; the response to `dp` can.
- **sensitivity** — a tornado on `s*`; rent-discretion `delta` is the widest swing.

Numbers are facts about this construction, not measurements of any economy. Seeded
(`SEED = 51721`, 60000 firms); rerun reproduces `results.json` exactly.
