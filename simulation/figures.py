"""Two figures for the paper. Pure matplotlib, serif, no seaborn.

  crossing.png        the crossover frontier and the population path
  identification.png  the regime comparison and the optionality/capture split
"""
from __future__ import annotations

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import analyses

INK = "#1a1a1a"
ACCENT = "#b3402f"   # hedge / access (warm)
COOL = "#2f6db3"     # exit / risk (cool)
GOLD = "#c8962a"
GREY = "#9aa0a6"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.edgecolor": INK,
    "axes.linewidth": 0.8,
    "axes.titlesize": 9.5,
    "figure.dpi": 150,
})


def plot_crossing(results: dict, path: pathlib.Path) -> None:
    th = results["threshold"]
    pa = results["path"]
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.0))

    # Left: s*(p) frontier for three mobility levels. Above a curve, hedge dominates
    # exit; below, exit dominates.
    ps = np.array(th["p_grid"])
    for key, color, lab in [("low_mobility", ACCENT, "low mobility m=0.25"),
                            ("mid_mobility", GOLD, "mid mobility m=0.55"),
                            ("high_mobility", COOL, "high mobility m=0.85")]:
        ys = np.array(th["by_mobility"][key], dtype=float)
        ys = np.clip(ys, 0, 1)
        axL.plot(ps, ys, color=color, lw=1.8, label=lab)
    axL.axhline(0.5, color=GREY, lw=0.7, ls=":")
    axL.set_xlim(0, 1); axL.set_ylim(0, 1)
    axL.set_xlabel("regime-change probability  $p$")
    axL.set_ylabel("state-dependence threshold  $s^{*}$")
    axL.set_title("Where access beats exit")
    axL.text(0.04, 0.93, "hedge dominates", color=ACCENT, fontsize=8)
    axL.text(0.60, 0.07, "exit dominates", color=COOL, fontsize=8)
    axL.legend(frameon=False, fontsize=7, loc="upper right")

    # Right: population strategy shares as p rises.
    pg = np.array(pa["p_grid"])
    axR.plot(pg, pa["hedge"], color=ACCENT, lw=2.0, label="hedge (buy access)")
    axR.plot(pg, pa["exit"], color=COOL, lw=2.0, label="exit (price risk)")
    axR.plot(pg, pa["voice"], color=GOLD, lw=1.4, label="voice (lobby)")
    axR.plot(pg, pa["stay"], color=GREY, lw=1.2, ls="--", label="stay")
    cx = pa.get("hedge_exceeds_exit_at_p")
    if cx is not None:
        axR.axvline(cx, color=INK, lw=0.7, ls=":")
        axR.text(cx + 0.01, 0.62, f"hedge > exit\nat p={cx:g}", fontsize=7, color=INK)
    axR.set_xlim(0, 1); axR.set_ylim(0, 1)
    axR.set_xlabel("regime-change probability  $p$")
    axR.set_ylabel("share of firms")
    axR.set_title("One probability, two responses")
    axR.legend(frameon=False, fontsize=7, loc="upper left")

    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_regime_map(results: dict, path: pathlib.Path) -> None:
    rm = results["regime_map"]
    deltas = np.array(rm["delta_grid"])
    ps = np.array(rm["p_grid"])
    Z = np.array(rm["intensity"])  # shape (len(deltas), len(ps))
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    extent = [ps.min(), ps.max(), deltas.min(), deltas.max()]
    im = ax.imshow(Z, origin="lower", extent=extent, aspect="auto",
                   cmap="YlOrRd", vmin=0, vmax=1)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("optionality intensity (normalized)", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    # named regimes as coordinates
    labels = {
        "norway": ("Norway", 0, 14, "left"),
        "eu_semiperiphery": ("EU semi-periphery\n(the worked case)", -2, 12, "left"),
        "consolidated": ("Hungary", 6, 6, "left"),
        "china": ("China", 6, -2, "left"),
        "russia": ("Russia", -6, -14, "right"),
        "gulf_rentier": ("Gulf rentier", -8, 6, "right"),
        "us_transactional": ("US transactional", 6, 0, "left"),
    }
    for key, r in rm["regimes"].items():
        ax.scatter([r["p"]], [r["delta"]], color=INK, s=26, zorder=5,
                   edgecolor="white", linewidth=0.6)
        if key in labels:
            txt, dx, dy, ha = labels[key]
            ax.annotate(txt, (r["p"], r["delta"]), textcoords="offset points",
                        xytext=(dx, dy), fontsize=7.2, color=INK, ha=ha)
    ax.set_xlim(0, 1.0); ax.set_ylim(0.05, 0.95)
    ax.set_xlabel("how settled the regime is  (probability $p$ $\\to$ 1)")
    ax.set_ylabel("rent-discretion  $\\delta$")
    ax.set_title("The space of regimes: where optionality is live")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_identification(results: dict, path: pathlib.Path) -> None:
    rg = results["regimes"]
    idn = results["identification"]
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.0))

    # Left: regime comparison, hedge vs exit mass.
    names = ["rising_semiperiphery", "consolidated", "mainstreamed"]
    labels = ["rising\nsemi-periphery", "consolidated", "mainstreamed"]
    x = np.arange(len(names))
    w = 0.36
    hedge = [rg[n]["hedge"] for n in names]
    exit_ = [rg[n]["exit"] for n in names]
    axL.bar(x - w / 2, hedge, w, color=ACCENT, label="hedge (access)")
    axL.bar(x + w / 2, exit_, w, color=COOL, label="exit (risk)")
    axL.set_xticks(x); axL.set_xticklabels(labels, fontsize=8)
    axL.set_ylabel("share of firms")
    axL.set_ylim(0, max(max(hedge), max(exit_)) * 1.25)
    axL.set_title("The same shock, three regimes")
    axL.legend(frameon=False, fontsize=7)
    for xi, (h, e) in enumerate(zip(hedge, exit_)):
        axL.text(xi - w / 2, h + 0.01, f"{h:.2f}", ha="center", fontsize=7, color=ACCENT)
        axL.text(xi + w / 2, e + 0.01, f"{e:.2f}", ha="center", fontsize=7, color=COOL)

    # Right: the hedge value as a function of p is a call (convex, reversible); the
    # cross-section at one p cannot tell option-buying from a sunk directional bet.
    ps = np.linspace(0, 1, 50)
    s_demo, m_demo = 0.55, 0.45
    Hs = [max(0.0, analyses.hedge_value(s_demo, p=p)) for p in ps]
    axR.plot(ps, Hs, color=ACCENT, lw=2.0, label="option value of access")
    p_hi, p_lo = idn["p_hi"], idn["p_lo"]
    axR.scatter([p_hi], [max(0.0, analyses.hedge_value(s_demo, p=p_hi))],
                color=INK, zorder=5, s=22)
    axR.scatter([p_lo], [max(0.0, analyses.hedge_value(s_demo, p=p_lo))],
                color=INK, zorder=5, s=22)
    axR.annotate("", xy=(p_lo, max(0.0, analyses.hedge_value(s_demo, p=p_lo))),
                 xytext=(p_hi, max(0.0, analyses.hedge_value(s_demo, p=p_hi))),
                 arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0))
    rev = idn["optionality_reversibility"]
    axR.text(0.30, max(Hs) * 0.78,
             f"probability recedes\n{rev:.0%} of hedges unwind\n(capture: 0%)",
             fontsize=7.5, color=INK)
    axR.set_xlim(0, 1)
    axR.set_xlabel("regime-change probability  $p$")
    axR.set_ylabel("value of access")
    axR.set_title("Optionality vs capture")
    axR.legend(frameon=False, fontsize=7, loc="upper left")

    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
