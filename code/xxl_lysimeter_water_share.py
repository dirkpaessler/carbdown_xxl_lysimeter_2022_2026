#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Irrigation-water (tap water) share in the XXL Lysimeter, Fürth 2022.

Two figures:
  1) water_irrigation_share_2022.png  — first-summer water balance (rain vs tap water)
     and the tap-water alkalinity input vs the measured leachate TA export per interval.
  2) TA_cumulative_gross_vs_net_tapwater.png — accumulated CDR per treatment, "as measured
     (gross)" vs "minus irrigation water (net)". The irrigation blank is common to every
     pot, so it shifts the whole pack down by the same ~0.6 tCO2e/ha and does NOT change the
     treatment-vs-control comparison.

Tap water (Infra Fürth, our zone, 2026): 16.7 dGH, ~5.1 mmol/L HCO3 (ion balance).
Irrigation per pot (logbook "Water Calculator"): ~111 L, essentially all in Jun-Aug 2022.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
FIG = OUT / "figures"

HCO3 = 5.09           # mmol/L bicarbonate in the tap water (ion balance)
AREA = 0.406          # m2 per pot
POT_M2_CALC = 0.5     # the Water Calculator used 0.5 m2 for rain->L; keep for that panel
TRSTYLE = {"Control": "#333333", "100 t/ha": "#56B4E9", "200 t/ha": "#0072B2",
           "400 t/ha": "#D55E00", "200 t/ha fine": "#009E73"}
# irrigation L/pot per sampling interval (keyed to interval END date)
IRRIG = {"2022-07-05": 9.75, "2022-07-18": 42.75, "2022-08-01": 58.5}


def _co2(mmol_m2):                       # mmol/m2 -> tCO2e/ha (1 mol CO2 / mol HCO3)
    return mmol_m2 * 44.009 / 1000 * 0.01


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 140, "font.size": 11,
                         "axes.grid": True, "grid.color": "#ececec",
                         "axes.spines.top": False, "axes.spines.right": False})
    import brand_standalone as brand
    FIG.mkdir(parents=True, exist_ok=True)

    ts = pd.read_csv(OUT / "xxl_lysimeter_TA_timeseries.csv", parse_dates=["date"])
    ts = ts[ts["soil"] == "FUERTH2022"].copy()

    # ---- cumulative tap-water alkalinity input, as a step over dates ----
    dates = np.sort(ts["date"].unique())
    inp_by_date = {pd.Timestamp(d): 0.0 for d in dates}
    for k, L in IRRIG.items():
        inp_by_date[pd.Timestamp(k)] = _co2(L * HCO3 / AREA)
    cum_input = pd.Series(inp_by_date).sort_index().cumsum()      # tCO2e/ha, by date

    # ============ FIGURE 1: first-summer water share ============
    site = ts.groupby("date").agg(flux=("TA_flux_mmol_per_m2_avgBD", "mean"),
                                  rain=("rain_interval_mm", "mean")).reset_index()
    s = site[site["date"].dt.year == 2022].copy()
    s["tapL"] = s["date"].dt.strftime("%Y-%m-%d").map(IRRIG).fillna(0.0)
    s["rainL"] = s["rain"] * POT_M2_CALC
    s["rain_share"] = 100 * s["rainL"] / (s["rainL"] + s["tapL"]).replace(0, np.nan)
    s["export"] = _co2(s["flux"])
    s["tap_input"] = _co2(s["tapL"] * HCO3 / AREA)
    lbl = s["date"].dt.strftime("%d %b")
    x = np.arange(len(s))

    fig, (a0, a1) = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
    a0.bar(x, s["rainL"], color="#56B4E9", label="rain")
    a0.bar(x, s["tapL"], bottom=s["rainL"], color="#D55E00", label="tap water (irrigation)")
    a0.set_ylim(0, 78)
    for xi, (rs, tl) in enumerate(zip(s["rain_share"], s["tapL"])):
        if tl > 0 and pd.notna(rs):
            a0.text(xi, s["rainL"].iloc[xi] + tl + 1.5, f"{rs:.0f}% rain", ha="center",
                    va="bottom", fontsize=8.5, color="#555")
    a0.set_ylabel("Water input (L per pot)")
    a0.set_title("First summer 2022: the pots were watered mostly with tap water\n"
                 "On the driest sampling intervals only 6–7 % of the input was rain",
                 fontsize=12.5)
    a0.legend(frameon=False, fontsize=9, loc="upper left")

    a1.bar(x - 0.2, s["tap_input"], 0.38, color="#D55E00", label="tap-water alkalinity IN")
    a1.bar(x + 0.2, s["export"], 0.38, color="#111111", label="leachate TA export OUT")
    a1.axvspan(0.5, 3.5, color="#D55E00", alpha=0.06)
    a1.set_ylim(0, 0.40)
    a1.text(0.6, 0.36, "irrigation loads the soil (input ≫ export)", fontsize=8.5,
            color="#D55E00", ha="left", va="top")
    a1.annotate("30 Aug storm (77 mm) flushes it out", (5, 0.223), (5.4, 0.31),
                fontsize=8.5, color="#333", ha="left",
                arrowprops=dict(arrowstyle="->", color="#333", lw=1))
    a1.set_ylabel("tCO₂e/ha per interval")
    a1.set_xticks(x); a1.set_xticklabels(lbl, rotation=0, fontsize=8.5)
    a1.set_title("During irrigation the tap water delivers far more alkalinity than leaves —\n"
                 "so a large part of the early export is tap water, not weathering",
                 fontsize=11)
    a1.legend(frameon=False, fontsize=9, loc="upper right")
    fig.text(0.5, 0.005, "Tap water: Infra Fürth, 16.7 °dGH, ≈5.1 mmol/L HCO₃⁻ (ion balance). "
             "Irrigation volumes from the logbook 'Water Calculator'. Export = site-mean, "
             "avgBD volume model.", ha="center", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, 0.03, 1, 1), h_pad=3.2)
    brand.add_logo(fig, ax=a0, loc="upper right", frac=0.13)
    p1 = FIG / "water_irrigation_share_2022.png"
    fig.savefig(p1, bbox_inches="tight"); plt.close(fig)

    # ============ FIGURE 2: accumulated CDR, gross vs net (with/without tap water) ============
    tg = (ts.groupby(["treatment_group_label", "date"])["TA_CO2cum_t_per_ha_avgBD"]
          .mean().reset_index())
    order = ["Control", "100 t/ha", "200 t/ha", "400 t/ha", "200 t/ha fine"]
    fig, (b0, b1) = plt.subplots(1, 2, figsize=(13.5, 5.4), sharey=True)
    for panel, net in ((b0, False), (b1, True)):
        for name in order:
            g = tg[tg["treatment_group_label"] == name].sort_values("date")
            y = g["TA_CO2cum_t_per_ha_avgBD"].values.astype(float)
            if net:
                y = y - g["date"].map(cum_input).values
            panel.plot(g["date"], y, "-", color=TRSTYLE[name], lw=1.9, label=name)
        panel.axhline(0, color="#999", lw=0.8, ls=":")
    b0.set_title("As measured (gross export)", fontsize=12)
    b1.set_title("Minus irrigation water (net weathering)", fontsize=12)
    b0.set_ylabel("Cumulative bicarbonate export, tCO₂e/ha")
    # shade the tap-water band on the gross panel
    b0.fill_between(cum_input.index, 0, -cum_input.values * 0 + cum_input.values,
                    color="#D55E00", alpha=0.0)  # placeholder (keep axes clean)
    b0.legend(frameon=False, fontsize=9, loc="upper left")
    fig.suptitle("Accumulated CDR with and without the tap-water blank — a common ~0.5 tCO₂e/ha "
                 "input (up to ~0.6 mass-balance ceiling) shifts every pot equally",
                 fontsize=13, weight="bold")
    fig.text(0.5, 0.005, "Net = gross − cumulative tap-water alkalinity input. Mass-balance "
             "ceiling 111 L/pot × 5.1 mmol/L HCO₃⁻ = 0.61 tCO₂e/ha (shown); conservatively "
             "~0.5 allowing for HCO₃ uncertainty and minor retention. Common to every pot, so "
             "it does NOT change treatment-vs-control (the dose result is unaffected). Net dips "
             "below zero in summer 2022 while the soil still holds the input, then recovers.",
             ha="center", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    brand.add_logo(fig, ax=b1, loc="lower right", frac=0.13)
    p2 = FIG / "TA_cumulative_gross_vs_net_tapwater.png"
    fig.savefig(p2, bbox_inches="tight"); plt.close(fig)

    print("wrote:", p1.name, "and", p2.name)


if __name__ == "__main__":
    main()
