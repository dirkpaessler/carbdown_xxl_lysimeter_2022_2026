#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dose-response endpoint figure (XXL Lysimeter, Fürth 2022).

Replaces the article-2 table: cumulative bicarbonate export per treatment at day 1,011
(the last date with the full n = 4), mean ± 95 % CI across the four replicate pots.
Point plot with a shaded control band — every treatment overlaps the control, i.e. no
dose separates the pots.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
FIG = OUT / "figures"
COL = "TA_CO2cum_t_per_ha_avgBD"
DAY = 1011
ORDER = ["Control", "100 t/ha", "200 t/ha", "400 t/ha", "200 t/ha fine"]
LABEL = {"Control": "Control", "100 t/ha": "100 t/ha", "200 t/ha": "200 t/ha",
         "400 t/ha": "400 t/ha", "200 t/ha fine": "FINE (200, fine)"}
TRSTYLE = {"Control": "#333333", "100 t/ha": "#56B4E9", "200 t/ha": "#0072B2",
           "400 t/ha": "#D55E00", "200 t/ha fine": "#009E73"}


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 150, "font.size": 11,
                         "axes.grid": True, "grid.color": "#ececec",
                         "axes.spines.top": False, "axes.spines.right": False})
    import brand_standalone as brand
    FIG.mkdir(parents=True, exist_ok=True)

    ts = pd.read_csv(OUT / "xxl_lysimeter_TA_timeseries.csv", parse_dates=["date"])
    ts = ts[(ts["soil"] == "FUERTH2022") & (ts["days"] == DAY)]
    stat = {}
    for name in ORDER:
        v = ts[ts["treatment_group_label"] == name][COL].dropna().values
        m, sd, n = v.mean(), v.std(ddof=1), len(v)
        stat[name] = (m, 1.96 * sd / np.sqrt(n))
    ctrl_m, ctrl_ci = stat["Control"]

    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    ys = np.arange(len(ORDER))[::-1]                       # Control at top
    ax.axvspan(ctrl_m - ctrl_ci, ctrl_m + ctrl_ci, color="#333333", alpha=0.10, lw=0)
    ax.axvline(ctrl_m, color="#333333", lw=1, ls="--", alpha=0.5)
    for y, name in zip(ys, ORDER):
        m, ci = stat[name]
        c = TRSTYLE[name]
        ax.errorbar(m, y, xerr=ci, fmt="o", color=c, ecolor=c, elinewidth=2.2,
                    capsize=5, capthick=2.2, ms=9, zorder=5)
        ax.text(m, y + 0.22, f"{m:.2f} ± {ci:.2f}", ha="center", va="bottom",
                fontsize=9.5, color=c, weight="bold")
    ax.set_yticks(ys); ax.set_yticklabels([LABEL[n] for n in ORDER])
    ax.set_ylim(-0.6, len(ORDER) - 0.2)
    ax.set_xlabel("Cumulative bicarbonate export, tCO₂e/ha")
    ax.set_title("By day 1,011 the control sits in the pack —\nno dose separates the pots",
                 fontsize=13, weight="bold")
    ax.text(0.99, 0.04, "grey band = control ± 95 % CI", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=8.5, color="#666")
    fig.text(0.5, 0.005, "Cumulative bicarbonate export at day 1,011 (last date with the full "
             "n = 4); point = treatment mean, bars = 95 % CI across the four replicate pots. "
             "Every treatment's interval overlaps the control band. Volume model avgBD.",
             ha="center", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    brand.add_logo(fig, ax=ax, loc="lower left", frac=0.14)
    p = FIG / "TA_endpoint_by_treatment.png"
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    print("wrote:", p.name, "| values:",
          {LABEL[n]: (round(stat[n][0], 2), round(stat[n][1], 2)) for n in ORDER})


if __name__ == "__main__":
    main()
