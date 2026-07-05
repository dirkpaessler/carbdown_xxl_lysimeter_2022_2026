#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XXL Lysimeter — narrative "story" figures of the key relationships found in the
in-situ sensor vs. leachate analysis. Run after xxl_lysimeter_monitoring.py.

Produces output/figures/story_1..5_*.png:
  1. In-situ 60 cm soil-EC sensor predicts leachate EC (continuous MRV proxy).
  2. The enhanced-weathering mechanism chain: temperature -> soil CO2 -> acidity & TA.
  3. Seasonal "breathing": CO2/temperature peak in summer, leachate pH dips.
  4. Soil moisture as a measurement confounder for EC (collapse + partial-corr fix).
  5. Soil CO2 by basalt dose over time (weak, single-pot hint of drawdown at 400 t/ha).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
FIG = OUT / "figures"
MON = HERE / "Monitoring"

OK = {"black": "#333333", "blue": "#0072B2", "sky": "#56B4E9", "orange": "#E69F00",
      "verm": "#D55E00", "green": "#009E73", "purple": "#CC79A7", "grey": "#999999"}
TRSTYLE = {"000": (OK["black"], "Control"), "100": (OK["sky"], "100 t/ha"),
           "200": (OK["blue"], "200 t/ha"), "400": (OK["verm"], "400 t/ha"),
           "FINE": (OK["green"], "200 t/ha fine")}


def _fit(ax, x, y, color, loc=(0.04, 0.95)):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 4:
        return
    r = np.corrcoef(x[m], y[m])[0, 1]
    b1, b0 = np.polyfit(x[m], y[m], 1)
    xs = np.array([x[m].min(), x[m].max()])
    ax.plot(xs, b0 + b1 * xs, "-", color=color, lw=2, zorder=5)
    ax.text(loc[0], loc[1], f"r = {r:+.2f}  (n={m.sum()})", transform=ax.transAxes,
            va="top", fontsize=10, color=color, weight="bold")


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 140, "font.size": 11,
                         "axes.grid": True, "grid.color": "#ececec",
                         "axes.spines.top": False, "axes.spines.right": False})
    import brand_standalone as brand
    FIG.mkdir(parents=True, exist_ok=True)

    paired = pd.read_csv(OUT / "monitoring_leachate_sensor_paired.csv", parse_dates=["date"])
    site = pd.read_csv(MON / "sensor_sitemean_weekly.csv", parse_dates=["date"]).set_index("date")
    potsens = pd.read_csv(MON / "sensor_potlevel_weekly.csv", parse_dates=["date"])
    wide = pd.read_csv(OUT / "xxl_lysimeter_data_wide.csv", parse_dates=["date"])
    old = wide[wide["soil"] == "FUERTH2022"]

    # per-date site-level leachate means (old pots) for clean mechanism scatters
    lea = old.groupby("date").agg(
        pH=("pH_field", "mean"), TA=("HCO3_umol_per_l", "mean"),
        EC=("EC_lab_uS_per_cm_25degC", "mean"), Si=("Si_umol_per_l", "mean")).reset_index()
    def match(col, tol=7):
        s = site[col].dropna()
        out = []
        for d in lea["date"]:
            dd = np.abs((s.index - d).days); j = int(dd.argmin())
            out.append(s.iloc[j] if dd[j] <= tol else np.nan)
        return out
    for c in ["soil_temp_30cm_C", "soil_co2_ppm", "soil_ec_60cm"]:
        lea[c] = match(c)

    # ===== FIGURE 1: in-situ EC sensor predicts leachate EC ===================
    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    for tr, (c, lab) in TRSTYLE.items():
        g = paired[(paired["treatment"] == tr)].dropna(subset=["EC_lab_uS_per_cm_25degC", "soil_ec_60cm"])
        ax.scatter(g["EC_lab_uS_per_cm_25degC"], g["soil_ec_60cm"], s=26, color=c,
                   alpha=0.6, edgecolors="none", label=lab)
    g = paired.dropna(subset=["EC_lab_uS_per_cm_25degC", "soil_ec_60cm"])
    _fit(ax, g["EC_lab_uS_per_cm_25degC"], g["soil_ec_60cm"], "#111111")
    ax.set_xlabel("Leachate EC (µS/cm) — measured at sampling")
    ax.set_ylabel("In-situ soil EC sensor at 60 cm")
    ax.set_title("An in-situ sensor that tracks the leachate\n"
                 "The 60 cm soil-EC probe follows leachate ionic strength in every treatment",
                 fontsize=12.5)
    ax.legend(frameon=False, fontsize=9, title="", loc="lower right")
    ax.text(0.5, -0.16, "Continuous, buried EC sensor → candidate proxy for leachate chemistry "
            "between samplings (for MRV). Pot-wise; stronger still after controlling for soil moisture.",
            transform=ax.transAxes, ha="center", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    brand.add_logo(fig, loc="upper right", frac=0.13)
    fig.savefig(FIG / "story_1_soilEC_predicts_leachateEC.png", bbox_inches="tight"); plt.close(fig)

    # ---- per-treatment sensor/leachate data (used by figures 2 and 2b) ----
    co2raw = pd.read_excel(MON / "co2_concentrations.xlsx")
    co2raw.columns = [str(c).strip() for c in co2raw.columns]
    co2raw["date"] = pd.to_datetime(co2raw["Zeitstempel"], errors="coerce").dt.normalize()

    def co2_series(tr):
        v = pd.to_numeric(co2raw[f"SoilCO2.{tr}.A"], errors="coerce")
        s = pd.Series(v.values, index=co2raw["date"]).dropna()
        s = s[(s >= 1) & (s <= 40000)]
        return s.groupby(level=0).mean()

    def near_series(s, dates, tol=10):
        s = s.dropna()
        out = []
        for d in dates:
            if s.empty:
                out.append(np.nan); continue
            dd = np.abs((s.index - d).days); j = int(dd.argmin())
            out.append(s.iloc[j] if dd[j] <= tol else np.nan)
        return out

    trs = ["000", "100", "200", "400"]     # FINE has no soil-CO₂ sensor
    per_tr = {}
    for tr in trs:
        le = (old[old["treatment"] == tr].groupby("date")
              .agg(pH=("pH_field", "mean"), TA=("HCO3_umol_per_l", "mean")).reset_index())
        le["co2"] = near_series(co2_series(tr), le["date"])
        le["temp"] = near_series(site["soil_temp_30cm_C"].dropna(), le["date"])
        per_tr[tr] = le

    # ===== FIGURE 2: mechanism chain, dots coloured by basalt dose, pooled fit =====
    stage2 = [("temp", "co2", "Soil temperature (°C)", "Soil CO₂ (ppm)",
               "warmer soil → more respiration → more CO₂"),
              ("co2", "pH", "Soil CO₂ (ppm)", "Leachate pH",
               "more CO₂ → carbonic acid → lower pH"),
              ("co2", "TA", "Soil CO₂ (ppm)", "Leachate alkalinity TA (µmol/l)",
               "more CO₂ → more weathering → more TA")]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))
    for ax, (xc, yc, xl, yl, sub) in zip(axes, stage2):
        xs_all, ys_all = [], []
        for tr in trs:
            c, lab = TRSTYLE[tr]
            g = per_tr[tr].dropna(subset=[xc, yc])
            ax.scatter(g[xc], g[yc], s=34, color=c, alpha=0.75, edgecolors="white",
                       linewidths=0.4, label=(lab if ax is axes[0] else None))
            xs_all.append(g[xc]); ys_all.append(g[yc])
        _fit(ax, pd.concat(xs_all), pd.concat(ys_all), "#111111")     # pooled trend + r (all doses)
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(sub, fontsize=10.5)
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("The enhanced-weathering engine, visible in the sensors:  "
                 "temperature → soil CO₂ → acidity & alkalinity", fontsize=13, weight="bold")
    fig.text(0.5, 0.01, "Dots coloured by basalt dose (soil CO₂ = each dose's own A-pot sensor; "
             "temperature = site mean; leachate pH/TA = per-treatment mean per sampling). Black "
             "line = pooled fit across all doses. Nearest sensor within ±10 days. FINE has no soil-CO₂ sensor.",
             ha="center", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    brand.add_logo(fig, ax=axes[1], loc="upper right", frac=0.30)
    fig.savefig(FIG / "story_2_weathering_mechanism_chain.png", bbox_inches="tight"); plt.close(fig)

    # ===== FIGURE 2b: mechanism chain SEPARATED BY TREATMENT (per-dose fits) =====
    stages = [("temp", "co2", "Soil temperature (°C, site)", "Soil CO₂ (ppm)",
               "temperature → soil CO₂"),
              ("co2", "pH", "Soil CO₂ (ppm)", "Leachate pH", "soil CO₂ → pH"),
              ("co2", "TA", "Soil CO₂ (ppm)", "Leachate TA (µmol/l)", "soil CO₂ → TA")]
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.0))
    for k, (xc, yc, xl, yl, ttl) in enumerate(stages):
        ax = axes[k]
        rlines = []
        for tr in trs:
            c, lab = TRSTYLE[tr]
            g = per_tr[tr].dropna(subset=[xc, yc])
            ax.scatter(g[xc], g[yc], s=26, color=c, alpha=0.6, edgecolors="none",
                       label=lab if k == 0 else None)
            if len(g) >= 5:
                b1, b0 = np.polyfit(g[xc], g[yc], 1)
                xs = np.array([g[xc].min(), g[xc].max()])
                ax.plot(xs, b0 + b1 * xs, "-", color=c, lw=1.8)
                r = np.corrcoef(g[xc], g[yc])[0, 1]
                rlines.append((c, f"{lab}: r={r:+.2f} (n={len(g)})"))
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(ttl, fontsize=10.5)
        y0 = 0.97
        for c, txt in rlines:
            ax.text(0.03, y0, txt, transform=ax.transAxes, va="top", fontsize=8, color=c)
            y0 -= 0.07
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("Enhanced-weathering chain, separated by basalt dose  "
                 "(soil-CO₂ sensor = one A-pot per dose; FINE has none)",
                 fontsize=13, weight="bold")
    fig.text(0.5, 0.01, "Leachate pH/TA = per-treatment mean per sampling; soil CO₂ = that "
             "treatment's own A-pot sensor (n=1, dies over time); soil temperature = site mean. "
             "Nearest sensor within ±10 days.", ha="center", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    brand.add_logo(fig, ax=axes[1], loc="upper right", frac=0.30)
    fig.savefig(FIG / "story_2b_mechanism_chain_by_treatment.png", bbox_inches="tight"); plt.close(fig)

    # ===== FIGURE 3: seasonal breathing time series ==========================
    fig, ax = plt.subplots(figsize=(12, 5.2))
    co2 = site["soil_co2_ppm"].dropna()
    ax.plot(co2.index, co2.values, "-", color=OK["green"], lw=1.6, label="soil CO₂ (ppm)")
    ax.set_ylabel("Soil CO₂ (ppm)", color=OK["green"]); ax.tick_params(axis="y", colors=OK["green"])
    ax.set_xlabel("Date")
    ax2 = ax.twinx()
    ph = lea.dropna(subset=["pH"]).sort_values("date")
    ax2.plot(ph["date"], ph["pH"], "o-", color=OK["purple"], ms=4, lw=1.4, label="leachate pH")
    ax2.set_ylabel("Leachate pH", color=OK["purple"]); ax2.tick_params(axis="y", colors=OK["purple"])
    ax.set_title("The soil breathes with the seasons\n"
                 "Soil CO₂ peaks in summer; the leachate pH dips in anti-phase", fontsize=12.5)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=9, loc="upper right")
    fig.tight_layout()
    brand.add_logo(fig, ax=ax, loc="lower right", frac=0.12)
    fig.savefig(FIG / "story_3_seasonal_breathing.png", bbox_inches="tight"); plt.close(fig)

    # ===== FIGURE 4: moisture confounder =====================================
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(12.5, 5), gridspec_kw=dict(width_ratios=[1.5, 1]))
    g = potsens.dropna(subset=["soil_ec_60cm", "soil_moisture_60cm_pct"])
    a0.scatter(g["soil_moisture_60cm_pct"], g["soil_ec_60cm"], s=12, color=OK["blue"],
               alpha=0.35, edgecolors="none")
    a0.axvline(10, color=OK["verm"], ls="--", lw=1.5)
    a0.text(10.3, a0.get_ylim()[1] * 0.92, "10 % VWC — below this the\nEC sensor loses contact",
            fontsize=8.5, color=OK["verm"])
    a0.set_xlabel("Soil moisture at 60 cm (% VWC)"); a0.set_ylabel("Soil EC sensor at 60 cm")
    a0.set_title("Bulk soil EC collapses when the soil dries out", fontsize=11)
    # raw vs partial bars
    labels = ["EC 30 cm", "EC 60 cm"]
    raw = [0.39, 0.71]; par = [0.55, 0.77]
    x = np.arange(2)
    a1.bar(x - 0.2, raw, 0.38, color=OK["grey"], label="raw r")
    a1.bar(x + 0.2, par, 0.38, color=OK["green"], label="controlling for moisture")
    for xi, (r, p) in enumerate(zip(raw, par)):
        a1.text(xi - 0.2, r + 0.01, f"{r:.2f}", ha="center", fontsize=9)
        a1.text(xi + 0.2, p + 0.01, f"{p:.2f}", ha="center", fontsize=9)
    a1.set_xticks(x); a1.set_xticklabels(labels); a1.set_ylim(0, 0.9)
    a1.set_ylabel("r: soil EC ↔ leachate EC"); a1.legend(frameon=False, fontsize=9)
    a1.set_title("Removing the moisture effect\nmakes the real signal stronger", fontsize=11)
    fig.suptitle("Soil moisture is a measurement confounder for EC/pH — filtered and controlled",
                 fontsize=13, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    brand.add_logo(fig, ax=a0, loc="upper right", frac=0.17)
    fig.savefig(FIG / "story_4_moisture_confounder.png", bbox_inches="tight"); plt.close(fig)

    # ===== FIGURE 5: soil CO2 by treatment over time =========================
    co2df = pd.read_excel(MON / "co2_concentrations.xlsx")
    co2df.columns = [str(c).strip() for c in co2df.columns]
    co2df["date"] = pd.to_datetime(co2df["Zeitstempel"], errors="coerce")
    fig, ax = plt.subplots(figsize=(12, 5.2))
    for tr, chan in [("000", "SoilCO2.000.A"), ("100", "SoilCO2.100.A"),
                     ("200", "SoilCO2.200.A"), ("400", "SoilCO2.400.A")]:
        v = pd.to_numeric(co2df[chan], errors="coerce")
        d = pd.DataFrame({"date": co2df["date"], "co2": v}).dropna()
        d = d[(d["co2"] >= 1) & (d["co2"] <= 40000)].sort_values("date")
        if d.empty:
            continue
        d["roll"] = d["co2"].rolling(5, center=True, min_periods=2).median()
        c, lab = TRSTYLE[tr]
        ax.scatter(d["date"], d["co2"], s=10, color=c, alpha=0.25, edgecolors="none")
        ax.plot(d["date"], d["roll"], "-", color=c, lw=2, label=f"{lab} (pot {tr}.A)")
    ax.set_ylabel("Soil CO₂ at ~20 cm (ppm)"); ax.set_xlabel("Date")
    ax.set_title("Soil CO₂ by basalt dose over time — a weak hint only\n"
                 "400 t/ha tends lowest (possible weathering CO₂ drawdown), but n = 1 pot/treatment",
                 fontsize=12)
    ax.legend(frameon=False, fontsize=9, ncol=2)
    ax.text(0.5, -0.16, "Single sensor per treatment (the A-pots), sensors died over time — "
            "suggestive, not conclusive; would need replicated soil-CO₂ sensors.",
            transform=ax.transAxes, ha="center", fontsize=8, color="#666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    brand.add_logo(fig, ax=ax, loc="upper right", frac=0.12)
    fig.savefig(FIG / "story_5_soilCO2_by_treatment.png", bbox_inches="tight"); plt.close(fig)

    print("Story figures written: story_1..5 in", FIG)


if __name__ == "__main__":
    main()
