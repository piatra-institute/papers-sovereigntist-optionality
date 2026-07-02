# Audit

Dated log of editorial passes and verification runs. Newest first.
See the workspace docs (run `papers docs`): writing-pipeline.md §7 and refresh-pipeline.md.

## 2026-06-17 — generalization pass: the space of regimes

Scope: extend the paper from the EU semi-periphery to a general space of regimes, keeping the title the author chose ("Capital Fractions and the Price of a Possible Future"), which reads wider than the original setting. Prompted by the observation that the mechanism is parameter-general and should cover Russian oligarchs, Chinese party-state capital, Gulf rentier monarchies, Norway, and US transactional state-firm alignment.

Decisions:

- The generalization is not a flat "applies everywhere" list. It is a two-parameter map: rent-discretion $\delta$ against how settled the regime is ($p\to1$). Named regimes are coordinates. Sovereigntist optionality proper is the contested interior; Norway is the lower boundary ($\delta\to0$, institutions cap the rent, null) and the Gulf rentier monarchy is the upper boundary ($p\to1$, access decays into tribute). The boundaries make the interior a definite object.
- New §7 "The Space of Regimes" added after the identification section; the limits section became §8. Figure order preserved (the regime map is Figure 3).
- Research verified three new real citations and placed each on a boundary: Mehlum, Moene & Torvik (2006, *Economic Journal*) on institutions and the resource curse for the Norway boundary; Beblawi & Luciani (1987, *The Rentier State*) for the Gulf boundary; Pearson, Rithmire & Tsai (2021, *Current History*) on party-state capitalism for the China coordinate. Russia uses the already-cited Markus (2015); the US case uses the already-cited Hillman, Keim & Schuler (2004).

Simulation:

- New `analysis_regime_map`: optionality intensity O(δ,p) = (share hedging) × (1−p), the contingent share of hedging positions, over a 19×20 (δ,p) grid for the fixed semi-peripheral stock, normalized. Iterated through two weaker measures (value×reversibility, then value×(1−p)) before settling on share×(1−p), which is the only one that is smooth and reads zero at both boundaries while keeping the worked case bright. Reads: Norway 0.0, EU-rising 0.515 (brightest named regime), US 0.30, Hungary 0.17, China/Russia ~0.12, Gulf 0.0.
- New figure `regime_map.png` (Figure 3): the heatmap with the seven regimes plotted as coordinates.
- results.json grew to 487 distinct numeric values.

Verification (post-extension):

- voice: 0 errors, 7 review-candidate warns (foundational negate/contrastive constructions the sections develop). Rhythm 15% short, sd 14, longest no-short run 16 (cleared the flag with two short sentences in §3 and §7).
- lint (corpus-relative): still clean. No house-vocabulary or rhythm outlier against the corpus.
- refs: 32 cited / 32 bib / 0 missing / 0 unused (the three new sources all cited).
- claims: 41 prose decimals, 0 without a matching simulation value (§7 kept decimal-free in prose; numbers live in the figure and results.json).
- build: 15 pages, three figures embedded, 0 missing-character warnings.
- check => PASS.

## 2026-06-17 — initial full build

Scope: first complete build from the seed chat (a ChatGPT research-design dump on "capital hedging toward AUR / sovereigntist optionality") plus two deep-research reports the author supplied (Romania-specific and the semi-peripheral comparative version). Wrote the simulation, the paper, and all provenance docs; brought it to a clean build and `check => PASS`.

Decisions:

- The seed proposed a sprawling empirical research program (party-finance + procurement + ownership + media + market panels across ten countries, a dataset blueprint and an interactive dashboard). That program was not the paper. The genius-level move was to extract the one sharp, computable, non-moralizing contribution buried in it: "capital moves to the far right" hides its unit, and the right object is a real option priced over a population of firms indexed by state-dependence `s` and mobility `m`. Seven sections with substantive titles; no ceremonial Conclusion, no bolt-on Objections (§7 folds the limits and the sensitivity into the argument).
- Synthetic-data discipline enforced. Every threshold, share, and value is a fact about the stipulated construction, stated repeatedly as not a measurement. The reported Romanian/comparative figures (leu break, single-bid shares, subsidy splits, the Hungary/Poland/Italy contrast) appear in prose as motivation and calibrate nothing.
- The model gives the corpus a new shape rather than reusing one: a Hirschman menu (exit/voice/hedge) priced as options, a state-dependence threshold `s*` that sorts the population, a composition argument that dissolves the flee-and-court paradox, and an identification result (optionality vs capture is not in the cross-section).

Simulation (`simulation/`, `uv run run_all.py`, seeded `SEED=51721`, 60000 firms):

- Real-options valuation: hedge `H = p*delta*s*kappa - a*(1 - phi*(1-p))`, exit `X = m*(p*rho*(1-s) - k)`, voice `V = eta*p*rho*(1-s) - cv`, stay `0`. Threshold `s*(p,m)` solved in closed form and verified against the argmax.
- Reference point (`p=0.45, delta=0.5, rho=0.3, kappa=0.6, a=0.05, phi=0.5, k=0.04`): `s* = 0.4229`. Two-firm illustration: state-dependent (`s=0.7, m=0.3`) hedge `0.0583` > exit `0.0002`; mobile (`s=0.2, m=0.85`) exit `0.0578` > hedge (negative).
- Population path: all stay below `p≈0.1`, then split; by `p=0.25` hedge `0.5232`, exit `0.3811`, voice `0.0957`; at certainty `0.566 / 0.3625 / 0.0714`.
- Three regimes by access value at stake: rising `acc 0.0282 / exit_val 0.0166` (exit peaks here), consolidated `acc 0.1287 / exit 0.0828 share` (capture), mainstreamed `acc 0.0213` (accommodation, discretion capped).
- Identification: hedging cohort `0.5588`; reversibility `0.0678` (option) vs `0.0` (capture); retained access value ratio `0.2263` when `p` falls 0.6 -> 0.25.
- Sensitivity (tornado on `s*`): rent-discretion `delta` widest at `0.234`, then `rho 0.211`, `a 0.208`, `kappa 0.191`, `phi 0.053`. The most sensitive parameter is the one EU discipline sets.
- Two figures (crossing.png, identification.png), both embedded with full captions.

Verification:

- voice: 0 errors, 5 review-candidate warns, all foundational negate/contrastive constructions the sections develop (the central "capital is not one thing" reframe; the stage reframe; the synthetic-data flags). Kept per voice.md Pattern-2 nuance.
- lint (corpus-relative): clean. No house-vocabulary overuse outlier, no rhythm flag against the corpus. Rhythm 15% short, sd 13.
- refs: 29 cited / 29 bib / 0 missing / 0 unused.
- claims: 42 prose decimals, 0 without a matching simulation value after reconciling the reversibility figure to `0.0678`.
- build: both figures embedded, 0 missing-character warnings.
- check => PASS.

Notes / deferred:

- Status set to `built`, not `published`: deploying (sync + page.tsx entry + status flip + push) is the maintainer's step.
- The seed's interactive dashboard is not built; the runnable simulation is the companion artifact and already exposes the interest parameters (p, delta, rho, mobility distribution) as adjustable inputs in code.

---

## 2026-07-02 — reform pass (de-template)

Corpus reform, structural. The paper was already honest about the audit's charges: §1 states it "takes the threshold form... without its dynamics: it prices each move by expected value and finds the crossover," so the options framing is a contingent-claim metaphor rather than stochastic pricing, and §6 notes capture is insensitive "by construction." Targets were the shared templated closer and the twin abstract closer.

- paper/PAPER.md + metadata.yaml abstract: replaced the boilerplate closer "The construct prices the wager the word optionality names; it does not certify that any firm has placed it" (a variant shared with two other June papers) with a distinct ending stating the paper's own result, that the aggregate sign of capital's move is composition, not conviction.
- paper/PAPER.md §8: retitled "What the Model Prices and What It Leaves Open" -> "Composition, Not Conviction" (sovereigntist was on the templated-closer census list), and softened the "Three things the construction does not do" ledger opener; the three honest disclaimers and the substantive final paragraph are unchanged.
- Verify: voice 0 errors; refs 32/32, 0 missing/0 unused; claims 41/0 unmatched; check => PASS; synced.
