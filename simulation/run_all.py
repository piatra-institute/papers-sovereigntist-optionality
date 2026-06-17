"""Entry point: regenerate output/results.json and the figures in one command.

    uv run run_all.py
"""
from __future__ import annotations

import json
import pathlib

import analyses
import figures

OUT = pathlib.Path(__file__).parent / "output"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    results = analyses.run()
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    figures.plot_crossing(results, OUT / "figures" / "crossing.png")
    figures.plot_identification(results, OUT / "figures" / "identification.png")
    figures.plot_regime_map(results, OUT / "figures" / "regime_map.png")
    n = sum(1 for _ in _walk_numbers(results))
    print(f"wrote results.json ({n} numeric values) and 3 figures to {OUT}")


def _walk_numbers(v):
    if isinstance(v, bool):
        return
    if isinstance(v, (int, float)):
        yield v
    elif isinstance(v, dict):
        for x in v.values():
            yield from _walk_numbers(x)
    elif isinstance(v, list):
        for x in v:
            yield from _walk_numbers(x)


if __name__ == "__main__":
    main()
