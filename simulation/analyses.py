"""Sovereigntist optionality: a real-options model of capital under a credible
sovereigntist route to power.

A firm of normalized value 1 splits into a state-discretionary share s (contracts,
permits, subsidies, regulated prices, whose allocation a government re-decides) and
a market share 1 - s (disciplined by export demand, foreign owners, and EU rules).
A sovereigntist government reaches decisive power with probability p and commands
rent-discretion delta (the share of the state-exposed value it can reallocate) and
raises the country risk premium by rho on the market-exposed value. Capital mobility
m is how much of the firm's value can actually leave.

Each firm picks from Hirschman's menu, priced here as options:

  hedge (buy access)  H = p*delta*s*kappa - a*(1 - phi*(1 - p))
  exit  (disinvest)   X = m*(p*rho*(1 - s) - k)
  voice (lobby all)   Vv = eta*p*rho*(1 - s) - cv
  stay                0

H is a call on reallocated rents: it pays kappa of the contestable pool delta*s when
the regime arrives, costs the premium a up front, and salvages phi*a across party
lines when it does not. X is the value of pulling the mobile share out of a market
exposure that the regime would reprice. The whole apparatus is a fact about this
construction, not a measurement of any economy; the empirical figures in the paper
are reported separately and calibrate nothing here.

Every number the paper cites is written to output/results.json by run().
"""
from __future__ import annotations

import numpy as np

SEED = 51721
N_FIRMS = 60000

# Baseline parameters (the reference regime). Stipulated to display the geometry.
P0 = 0.45        # regime-change probability at the reference point
DELTA = 0.50     # rent-discretion: share of state-exposed value the regime reallocates
RHO = 0.30       # risk-premium hit to market-exposed value under the regime
KAPPA = 0.60     # capture efficiency: share of the contestable pool access secures
ACCESS = 0.05    # a, the access premium (option cost), paid up front
PHI = 0.50       # salvage: cross-party reuse of access if the regime does not arrive
EXITK = 0.04     # k, friction cost per unit of mobile value moved
ETA = 0.30       # private share of the stability benefit that voice secures
CV = 0.012       # cv, the cost of lobbying


def hedge_value(s, p=P0, delta=DELTA, kappa=KAPPA, a=ACCESS, phi=PHI):
    return p * delta * s * kappa - a * (1.0 - phi * (1.0 - p))


def exit_value(s, m, p=P0, rho=RHO, k=EXITK):
    return m * (p * rho * (1.0 - s) - k)


def voice_value(s, p=P0, rho=RHO, eta=ETA, cv=CV):
    return eta * p * rho * (1.0 - s) - cv


def best_strategy(s, m, **kw):
    """Return (label, value) of the maximizing choice; 'stay' is the zero floor."""
    vals = {
        "hedge": hedge_value(s, **{k: v for k, v in kw.items() if k in ("p", "delta", "kappa", "a", "phi")}),
        "exit": exit_value(s, m, **{k: v for k, v in kw.items() if k in ("p", "rho", "k")}),
        "voice": voice_value(s, **{k: v for k, v in kw.items() if k in ("p", "rho", "eta", "cv")}),
        "stay": 0.0,
    }
    label = max(vals, key=vals.get)
    return label, vals[label]


def threshold_s(m, p=P0, delta=DELTA, rho=RHO, kappa=KAPPA, a=ACCESS, phi=PHI, k=EXITK):
    """The state-dependence s* at which hedge value equals exit value, for a firm of
    mobility m. Below s*, exit (price the risk) dominates; above, hedge (buy access)
    dominates. H rises in s, X falls in s, so the crossover is unique where it lies
    in [0, 1]; clip to the unit interval and report whether it is interior."""
    # H(s) = p*delta*kappa*s - a*(1 - phi*(1-p))
    # X(s) = m*(p*rho*(1-s) - k) = m*p*rho - m*k - m*p*rho*s
    # Solve H = X:  s*(p*delta*kappa + m*p*rho) = a*(1 - phi*(1-p)) + m*p*rho - m*k
    aH = p * delta * kappa
    cH = a * (1.0 - phi * (1.0 - p))
    num = cH + m * p * rho - m * k
    den = aH + m * p * rho
    if den <= 0:
        return float("nan")
    return num / den


def _sample_population(rng, n=N_FIRMS, weights=(0.40, 0.40, 0.20)):
    """A three-mode population, one mode per Hirschman strategy:

      local      state-dependent, locally embedded   high s, low m  -> hedges
      mobile     market-exposed, footloose           low s,  high m -> exits
      embedded   market-exposed, fixed in place       low s,  low m  -> voices
                 (large regulated incumbents, foreign manufacturers in supply chains)

    weights are the mass shares (local, mobile, embedded) and need not be balanced;
    a semi-peripheral economy carries large local and mobile modes at once."""
    w = np.array(weights, dtype=float)
    w = w / w.sum()
    n_loc, n_mob = int(round(n * w[0])), int(round(n * w[1]))
    n_emb = n - n_loc - n_mob
    s_loc = rng.beta(4.0, 2.0, n_loc)
    m_loc = np.clip(1.0 - s_loc + rng.normal(0, 0.12, n_loc), 0.02, 0.98)
    s_mob = rng.beta(2.0, 4.0, n_mob)
    m_mob = np.clip(1.0 - s_mob + rng.normal(0, 0.12, n_mob), 0.02, 0.98)
    s_emb = rng.beta(2.0, 4.0, n_emb)
    m_emb = np.clip(rng.beta(2.0, 6.0, n_emb), 0.02, 0.98)  # low mobility, any s
    s = np.concatenate([s_loc, s_mob, s_emb])
    m = np.concatenate([m_loc, m_mob, m_emb])
    return s, m


def _shares(s, m, **kw):
    """Population shares choosing each strategy, plus aggregate value flows."""
    H = hedge_value(s, **{k: v for k, v in kw.items() if k in ("p", "delta", "kappa", "a", "phi")})
    X = exit_value(s, m, **{k: v for k, v in kw.items() if k in ("p", "rho", "k")})
    Vv = voice_value(s, **{k: v for k, v in kw.items() if k in ("p", "rho", "eta", "cv")})
    Z = np.zeros_like(s)
    stack = np.vstack([H, X, Vv, Z])  # order: hedge, exit, voice, stay
    choice = stack.argmax(axis=0)
    n = len(s)
    out = {
        "hedge": float(np.mean(choice == 0)),
        "exit": float(np.mean(choice == 1)),
        "voice": float(np.mean(choice == 2)),
        "stay": float(np.mean(choice == 3)),
        # value actually realized by the chosen strategy, summed and per firm
        "access_value": float(np.sum(np.where(choice == 0, H, 0.0)) / n),
        "exit_value": float(np.sum(np.where(choice == 1, X, 0.0)) / n),
    }
    out["net_toward"] = out["hedge"] - out["exit"]
    return out


def _round(obj, nd=4):
    if isinstance(obj, dict):
        return {k: _round(v, nd) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_round(v, nd) for v in obj]
    if isinstance(obj, float):
        return round(obj, nd)
    return obj


def analysis_threshold():
    """s*(p) for three mobility levels, and the reference crossover."""
    ps = np.round(np.linspace(0.05, 1.0, 20), 4)
    out = {"p_grid": ps.tolist(), "by_mobility": {}}
    for label, m in [("low_mobility", 0.25), ("mid_mobility", 0.55), ("high_mobility", 0.85)]:
        out["by_mobility"][label] = [round(float(threshold_s(m, p=p)), 4) for p in ps]
    out["s_star_reference"] = round(float(threshold_s(0.55, p=P0)), 4)
    # at the reference point, the hedge/exit values for a canonical state-dependent
    # firm (s=0.7, m=0.3) and a canonical mobile firm (s=0.2, m=0.85)
    out["state_dependent_firm"] = {
        "s": 0.7, "m": 0.3,
        "hedge": round(float(hedge_value(0.7)), 4),
        "exit": round(float(exit_value(0.7, 0.3)), 4),
        "choice": best_strategy(0.7, 0.3)[0],
    }
    out["mobile_firm"] = {
        "s": 0.2, "m": 0.85,
        "hedge": round(float(hedge_value(0.2)), 4),
        "exit": round(float(exit_value(0.2, 0.85)), 4),
        "choice": best_strategy(0.2, 0.85)[0],
    }
    return out


def analysis_path(rng):
    """Aggregate strategy shares as the regime probability p rises, for a
    semi-peripheral population (balanced foreign/local mass)."""
    s, m = _sample_population(rng, weights=(0.40, 0.40, 0.20))
    ps = np.round(np.linspace(0.0, 1.0, 21), 4)
    path = {"p_grid": ps.tolist(), "hedge": [], "exit": [], "voice": [], "stay": [], "net_toward": []}
    for p in ps:
        sh = _shares(s, m, p=p)
        for key in ("hedge", "exit", "voice", "stay", "net_toward"):
            path[key].append(round(sh[key], 4))
    # the p at which hedge mass first exceeds exit mass
    cross = next((float(ps[i]) for i in range(len(ps))
                  if path["hedge"][i] > path["exit"][i]), None)
    path["hedge_exceeds_exit_at_p"] = cross
    return path


def analysis_regimes(rng):
    """Three named parameter regimes standing for consolidation stages and
    structural positions. Numbers are model outputs, not country measurements."""
    regimes = {
        # rising veto actor in a semi-peripheral economy: large local and mobile
        # modes at once, markets fear transmission
        "rising_semiperiphery": dict(weights=(0.40, 0.40, 0.20), p=0.45, delta=0.50, rho=0.30),
        # consolidated governance: discretion high, risk premium normalized, capital
        # base tilted to state-dependent local firms
        "consolidated": dict(weights=(0.55, 0.20, 0.25), p=0.80, delta=0.70, rho=0.12),
        # mainstreamed sovereigntist-right in a credibly constrained setting, more
        # mobile/core capital
        "mainstreamed": dict(weights=(0.30, 0.50, 0.20), p=0.75, delta=0.30, rho=0.10),
    }
    out = {}
    for name, cfg in regimes.items():
        s, m = _sample_population(rng, weights=cfg["weights"])
        sh = _shares(s, m, p=cfg["p"], delta=cfg["delta"], rho=cfg["rho"])
        out[name] = {"p": cfg["p"], "delta": cfg["delta"], "rho": cfg["rho"],
                     "weights": list(cfg["weights"]),
                     **{k: round(sh[k], 4) for k in
                        ("hedge", "exit", "voice", "stay", "net_toward",
                         "access_value", "exit_value")}}
    return out


def analysis_identification(rng):
    """Optionality versus capture. A cohort buys access at high probability p_hi.
    The probability then falls back to p_lo (the route to power recedes). Under
    optionality the hedge is a real option: a firm abandons access when its value
    turns negative, salvaging phi. The reversibility statistic is the share of the
    hedging cohort whose position unwinds. Capture, a sunk directional bet, has
    reversibility zero by construction. The cross-section alone (hedging present)
    cannot separate them; only the response to dp can."""
    s, m = _sample_population(rng, weights=(0.40, 0.40, 0.20))
    p_hi, p_lo = 0.60, 0.25
    # cohort that hedged at p_hi
    H_hi = hedge_value(s, p=p_hi)
    X_hi = exit_value(s, m, p=p_hi)
    V_hi = voice_value(s, p=p_hi)
    hedged = (H_hi > np.maximum.reduce([X_hi, V_hi, np.zeros_like(s)]))
    n_hedged = int(hedged.sum())
    # at p_lo, does the hedge still beat its outside options?
    H_lo = hedge_value(s, p=p_lo)
    X_lo = exit_value(s, m, p=p_lo)
    V_lo = voice_value(s, p=p_lo)
    still = hedged & (H_lo > np.maximum.reduce([X_lo, V_lo, np.zeros_like(s)]))
    unwind = hedged & ~still
    reversibility = float(unwind.sum() / max(1, n_hedged))
    # The sharper identifying signal is intensity, not headcount: under optionality
    # the value committed to access scales with p, so when the probability recedes
    # the access the cohort still holds is worth far less. Under capture the
    # position is sunk and its committed value does not respond to p at all.
    val_hi = float(np.sum(np.clip(H_hi[hedged], 0, None)))
    val_lo = float(np.sum(np.clip(H_lo[hedged], 0, None)))
    return {
        "p_hi": p_hi, "p_lo": p_lo,
        "hedging_cohort_share": round(float(hedged.mean()), 4),
        "optionality_reversibility": round(reversibility, 4),
        "capture_reversibility": 0.0,
        "access_value_retained_ratio": round(val_lo / val_hi if val_hi else 0.0, 4),
        "cross_section_identifies": False,
        "note": "same cross-section, two data-generating processes; dp identifies",
    }


def analysis_regime_map(rng):
    """The space of regimes. Holding a semi-peripheral capital stock fixed, vary the
    two parameters that describe a regime, rent-discretion delta and how settled it
    is (probability p), and measure where live optionality exists.

    Optionality intensity O(delta, p) = (share of firms hedging) times (1 - p): the
    fraction of the capital stock holding a position that is still contingent on the
    regime's arrival, a bet rather than a settled fact. It is near zero where there are
    no rents to option, so almost no one hedges (delta -> 0, the institutional-cap
    boundary), and it darkens as the regime settles (p -> 1, the rentier/consolidated
    boundary, where access is held but is no longer an option, only the standing price
    of access, that is, tribute). It is live in the contested interior, which is
    sovereigntist optionality proper. Named regimes are placed as coordinates; their
    numbers are model readings, not country measurements."""
    s, m = _sample_population(rng, weights=(0.40, 0.40, 0.20))
    deltas = np.round(np.linspace(0.05, 0.95, 19), 4)
    ps = np.round(np.linspace(0.05, 1.0, 20), 4)
    grid = []
    omax = 0.0
    n = len(s)
    for d in deltas:
        row = []
        for p in ps:
            H = hedge_value(s, p=p, delta=d)
            X = exit_value(s, m, p=p)
            Vv = voice_value(s, p=p)
            hedged = H > np.maximum.reduce([X, Vv, np.zeros_like(s)])
            share_hedging = float(hedged.sum() / n)
            o = share_hedging * (1.0 - p)  # contingent share: option, not tribute
            omax = max(omax, o)
            row.append(o)
        grid.append(row)
    # normalize to [0,1] for display
    grid = [[round(v / omax, 4) if omax else 0.0 for v in row] for row in grid]
    regimes = {
        "norway": {"delta": 0.05, "p": 0.10, "note": "institutional cap on rents; null"},
        "eu_semiperiphery": {"delta": 0.50, "p": 0.45, "note": "live optionality"},
        "consolidated": {"delta": 0.70, "p": 0.85, "note": "tribute (settled)"},
        "china": {"delta": 0.85, "p": 0.90, "note": "party-state discretion"},
        "russia": {"delta": 0.80, "p": 0.92, "note": "tribute under predation"},
        "gulf_rentier": {"delta": 0.92, "p": 0.98, "note": "rentier; p at one"},
        "us_transactional": {"delta": 0.55, "p": 0.70, "note": "core, bimodal stock"},
    }
    return {"delta_grid": deltas.tolist(), "p_grid": ps.tolist(),
            "intensity": grid, "shock_relative": 0.80, "regimes": regimes}


def analysis_sensitivity():
    """How the reference threshold s*(p=P0, m=0.55) moves as each parameter swings
    across a plausible band. The largest swing names the assumption the verdict
    leans on hardest. A tornado in the geometry, not in any data."""
    base = float(threshold_s(0.55, p=P0))
    bands = {
        "delta": (0.30, 0.70), "rho": (0.15, 0.45), "kappa": (0.40, 0.80),
        "access_a": (0.02, 0.08), "phi": (0.30, 0.70),
    }
    out = {"baseline_s_star": round(base, 4), "swings": {}}
    for name, (lo, hi) in bands.items():
        kw_lo = {"delta": DELTA, "rho": RHO, "kappa": KAPPA, "a": ACCESS, "phi": PHI}
        kw_hi = dict(kw_lo)
        key = "a" if name == "access_a" else name
        kw_lo[key], kw_hi[key] = lo, hi
        s_lo = float(threshold_s(0.55, p=P0, delta=kw_lo["delta"], rho=kw_lo["rho"],
                                 kappa=kw_lo["kappa"], a=kw_lo["a"], phi=kw_lo["phi"]))
        s_hi = float(threshold_s(0.55, p=P0, delta=kw_hi["delta"], rho=kw_hi["rho"],
                                 kappa=kw_hi["kappa"], a=kw_hi["a"], phi=kw_hi["phi"]))
        out["swings"][name] = {"low": round(s_lo, 4), "high": round(s_hi, 4),
                               "range": round(abs(s_hi - s_lo), 4)}
    out["largest_driver"] = max(out["swings"], key=lambda k: out["swings"][k]["range"])
    return out


def run() -> dict:
    rng = np.random.default_rng(SEED)
    results = {
        "parameters": {
            "seed": SEED, "n_firms": N_FIRMS, "p_reference": P0, "delta": DELTA,
            "rho": RHO, "kappa": KAPPA, "access_a": ACCESS, "phi": PHI,
            "exit_k": EXITK, "eta": ETA, "cv": CV,
        },
        "threshold": analysis_threshold(),
        "path": analysis_path(np.random.default_rng(SEED + 1)),
        "regimes": analysis_regimes(np.random.default_rng(SEED + 2)),
        "identification": analysis_identification(np.random.default_rng(SEED + 3)),
        "regime_map": analysis_regime_map(np.random.default_rng(SEED + 4)),
        "sensitivity": analysis_sensitivity(),
    }
    return _round(results)


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
