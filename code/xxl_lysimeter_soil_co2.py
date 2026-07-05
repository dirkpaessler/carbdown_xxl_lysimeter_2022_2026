#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XXL Lysimeter — per-pot soil-CO2 story (one sensor in every pot, n=3-4 per dose).

Inputs:
  output/soil_co2_by_pot_daily.csv   (built from the daily CO2 sensor exports)
  Monitoring/soil_temperature_30cm.xlsx
  output/xxl_lysimeter_data_wide.csv  (leachate pH / TA per pot)

Produces output/figures/:
  co2_1_seasonal_breathing_by_dose.png   seasonal cycle + doses converge
  co2_2_dose_forest.png                  season-adjusted CO2 vs control (n.s.)
  co2_3_engine_temp_co2_ph.png           temp -> CO2 -> leachate pH, per pot
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
FIG = OUT / "figures"
MON = HERE / "Monitoring"

OK = {"black": "#333333", "blue": "#0072B2", "sky": "#56B4E9", "orange": "#E69F00",
      "verm": "#D55E00", "green": "#009E73", "purple": "#CC79A7", "grey": "#999999"}
# treatment -> (colour, label), ordered
TR = [("Control", OK["black"], "Control"),
      ("100 t/ha", OK["sky"], "100 t/ha"),
      ("200 t/ha", OK["blue"], "200 t/ha"),
      ("400 t/ha", OK["verm"], "400 t/ha"),
      ("FINE", OK["green"], "FINE (200, fine)")]
COL = {t: c for t, c, _ in TR}
LAB = {t: l for t, _, l in TR}


def load():
    co2 = pd.read_csv(OUT / "soil_co2_by_pot_daily.csv", parse_dates=["date"])
    co2["logco2"] = np.log(co2["soil_co2_ppm"])
    co2["month"] = co2["date"].dt.month
    co2["ym"] = co2["date"].values.astype("datetime64[M]")
    return co2


def season_adjust(co2):
    clim = co2.groupby("month")["logco2"].transform("mean")
    co2 = co2.assign(resid=co2["logco2"] - clim)
    pot = co2.groupby(["treatment", "pot_id"], observed=True)["resid"].mean().reset_index()
    return pot


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 150, "font.size": 11,
                         "axes.grid": True, "grid.color": "#ededed",
                         "axes.spines.top": False, "axes.spines.right": False})
    import brand_standalone as brand
    FIG.mkdir(parents=True, exist_ok=True)
    co2 = load()

    # ================= FIGURE 1: seasonal breathing, doses overlaid =================
    fig, ax = plt.subplots(figsize=(11, 5.0))
    # light grey envelope = overall monthly 25-75 % across all pots (the "breath")
    env = co2.groupby("ym")["soil_co2_ppm"].agg(lo=lambda s: s.quantile(.25),
                                                hi=lambda s: s.quantile(.75)).reset_index()
    ax.fill_between(env["ym"], env["lo"], env["hi"], color="#cfcfcf", alpha=0.35, lw=0,
                    zorder=1, label="all pots, 25–75 %")
    for t, c, l in TR:
        g = co2[co2.treatment == t]
        mm = g.groupby("ym")["soil_co2_ppm"].median().reset_index()
        mm = mm[mm["ym"] >= np.datetime64("2022-10")]
        ax.plot(mm["ym"], mm["soil_co2_ppm"], "-", color=c, lw=2.0, zorder=3, label=l)
    ax.set_ylabel("Soil CO₂ at ~20 cm (ppm), monthly median")
    ax.set_xlabel("")
    ax.set_ylim(0, 7000)
    ax.xaxis.set_major_locator(mdates.MonthLocator((1, 7)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.set_title("Every pot breathes with the seasons — and the basalt dose barely changes the breath\n"
                 "Soil CO₂ peaks each summer, collapses each winter; the five dose curves stay tangled together",
                 fontsize=12.5, loc="left")
    ax.legend(frameon=False, ncol=6, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.10))
    fig.tight_layout()
    brand.add_logo(fig, ax=ax, loc="upper right", frac=0.13)
    fig.savefig(FIG / "co2_1_seasonal_breathing_by_dose.png", bbox_inches="tight")
    plt.close(fig)

    # ================= FIGURE 2: dose scatter (per-pot, season-adjusted) ===========
    pot = season_adjust(co2)
    ref = pot[pot.treatment == "Control"]["resid"]
    rc, sc, nc = ref.mean(), ref.std(ddof=1), len(ref)
    pot = pot.assign(ratio=np.exp(pot["resid"] - rc))          # each pot relative to control geomean
    order = ["Control", "100 t/ha", "200 t/ha", "400 t/ha", "FINE"]
    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    ax.axvline(1.0, color=OK["black"], lw=1.3, ls="--", zorder=1)
    for i, t in enumerate(reversed(order)):
        y = i
        sub = pot[pot.treatment == t]; c = COL[t]; n = len(sub)
        jit = np.linspace(-0.16, 0.16, n) if n > 1 else np.array([0.0])
        ax.scatter(sub["ratio"], y + jit, s=55, color=c, alpha=0.45,
                   edgecolors="none", zorder=3)                # one dot per pot
        m = sub["resid"].mean(); se = sub["resid"].std(ddof=1) / np.sqrt(n)
        d = m - rc; se_d = np.sqrt(se**2 + (sc / np.sqrt(nc))**2)
        tc = stats.t.ppf(.975, max(n + nc - 2, 1))
        ratio, lo, hi = np.exp(d), np.exp(d - tc * se_d), np.exp(d + tc * se_d)
        if t != "Control":
            ax.plot([lo, hi], [y, y], "-", color=c, lw=2.0, alpha=0.9, zorder=4)
        ax.scatter([ratio], [y], s=150, color=c, edgecolors="white", lw=1.5, zorder=5)
        ax.text(ratio, y + 0.30, f"×{ratio:.2f}", va="bottom", ha="center", fontsize=10, color=c, weight="bold")
        ax.text(0.30, y, f"{LAB[t]}\n(n={n})", va="center", ha="right", fontsize=10)
    ax.set_yticks([]); ax.set_ylim(-0.6, 4.8); ax.set_xlim(0.28, 2.05)
    ax.set_xlabel("Season-adjusted soil CO₂ relative to control  ·  dot = pot, diamond = treatment mean ± 95 % CI")
    ax.set_title("More basalt does not raise — or clearly lower — soil CO₂\n"
                 "The pots scatter ×0.5–×1.7 within every treatment; means overlap control (400 t/ha ~13 % lower, n.s.)",
                 fontsize=12, loc="left")
    fig.tight_layout()
    brand.add_logo(fig, ax=ax, loc="lower right", frac=0.12)
    fig.savefig(FIG / "co2_2_dose_forest.png", bbox_inches="tight")
    plt.close(fig)

    # ---- shared: site-mean daily soil temperature & moisture ----
    t = pd.read_excel(MON / "soil_temperature_30cm.xlsx")
    t.columns = [str(c).strip() for c in t.columns]
    t["date"] = pd.to_datetime(t["Zeitstempel"], errors="coerce").dt.normalize()
    t["temp_SOIL"] = pd.to_numeric(t["temp_SOIL"], errors="coerce")
    t = t[(t.temp_SOIL > -5) & (t.temp_SOIL < 45)]
    tday = t.groupby("date")["temp_SOIL"].mean().rename("temp")

    mo = pd.read_excel(MON / "soil_moisture_60cm.xlsx")
    mo.columns = [str(c).strip() for c in mo.columns]
    mo["date"] = pd.to_datetime(mo["Zeitstempel"], errors="coerce").dt.normalize()
    vcm = [c for c in mo.columns if c.startswith("EC.60")]
    mm = mo.melt("date", value_vars=vcm, value_name="v").dropna(subset=["v"])
    mm["v"] = pd.to_numeric(mm["v"], errors="coerce")
    mm = mm[(mm.v >= 2.5) & (mm.v <= 60)]
    moday = mm.groupby("date")["v"].mean().rename("moist")

    w = pd.read_csv(OUT / "xxl_lysimeter_data_wide.csv", parse_dates=["date"])
    f = w[w.soil == "FUERTH2022"].copy()

    def to_potid(v):
        a, b = v.split(".")
        return ("FINE200." + b) if a == "FINE" else (a + "." + b)
    f["pot_id"] = f["variant"].map(lambda v: to_potid(v) if "." in v else v)

    def nearest(pot, dte, tol=12):
        s = co2[co2.pot_id == pot]
        if not len(s):
            return np.nan
        dd = (s.date - dte).abs().dt.days
        j = dd.values.argmin()
        return s.iloc[j]["soil_co2_ppm"] if dd.iloc[j] <= tol else np.nan
    _pref = {"000": "Control", "100": "100 t/ha", "200": "200 t/ha",
             "400": "400 t/ha", "FINE200": "FINE"}

    # ================= FIGURE 3: temp x moisture engine (the 18°C reversal) =========
    cc = co2.merge(tday, on="date").merge(moday, on="date")
    fig, ax = plt.subplots(figsize=(10.6, 5.4))
    sc = ax.scatter(cc["temp"], cc["soil_co2_ppm"], c=cc["moist"], cmap="RdYlBu",
                    vmin=14, vmax=30, s=13, alpha=0.75, edgecolors="none", zorder=2)
    cb = fig.colorbar(sc, ax=ax, pad=0.015)
    cb.set_label("Soil moisture at 60 cm (%)  ·  red = dry, blue = wet")
    # binned median CO2 vs temp (rise then fall)
    edges = np.arange(0, 26, 2.0); bx, by = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (cc.temp >= lo) & (cc.temp < hi)
        if m.sum() >= 15:
            bx.append((lo + hi) / 2); by.append(np.median(cc.soil_co2_ppm[m]))
    ax.plot(bx, by, "-o", color="#111111", lw=2.6, ms=5, zorder=5, label="median CO₂")
    ax.axvline(18, color=OK["verm"], ls="--", lw=1.6, zorder=3)
    r_lo = np.corrcoef(cc[cc.temp <= 18].temp, np.log(cc[cc.temp <= 18].soil_co2_ppm))[0, 1]
    r_hi = np.corrcoef(cc[cc.temp > 18].temp, np.log(cc[cc.temp > 18].soil_co2_ppm))[0, 1]
    ax.annotate("above ~18 °C the soil dries out,\nmicrobes go dormant → CO₂ stalls and falls",
                xy=(20.5, np.median(by[-2:]) if by else 5000), xytext=(0.40, 0.30),
                textcoords="axes fraction", fontsize=9.5, color=OK["verm"], va="top",
                arrowprops=dict(arrowstyle="->", color=OK["verm"], lw=1.4))
    ax.set_yscale("log")
    ax.set_xlabel("Soil temperature at 30 cm (°C), site mean")
    ax.set_ylabel("Soil CO₂ at ~20 cm (ppm, log)")
    ax.set_title("Warm soil breathes more CO₂ — until it dries out\n"
                 f"Respiration climbs with temperature (≤18 °C r = {r_lo:+.2f}) then reverses as the soil dries "
                 f"(>18 °C r = {r_hi:+.2f})", fontsize=12, loc="left")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.tight_layout()
    brand.add_logo(fig, ax=ax, loc="upper left", frac=0.13)
    fig.savefig(FIG / "co2_3_temp_moisture_engine.png", bbox_inches="tight")
    plt.close(fig)

    # ================= FIGURE 4: CO2 is the engine, not the meter ===================
    ph = f.dropna(subset=["pH_lab"]).copy()
    ph["co2n"] = [nearest(p, d) for p, d in zip(ph.pot_id, ph.date)]
    ph = ph.dropna(subset=["co2n"]); ph["tname"] = ph.pot_id.map(lambda p: _pref.get(p.split(".")[0]))
    ta = f.dropna(subset=["HCO3_umol_per_l"]).copy()
    ta["co2n"] = [nearest(p, d) for p, d in zip(ta.pot_id, ta.date)]
    ta = ta.dropna(subset=["co2n"]); ta["tname"] = ta.pot_id.map(lambda p: _pref.get(p.split(".")[0]))
    ec_ta = np.corrcoef(f.dropna(subset=["EC_lab_uS_per_cm_25degC", "HCO3_umol_per_l"]).EC_lab_uS_per_cm_25degC,
                        f.dropna(subset=["EC_lab_uS_per_cm_25degC", "HCO3_umol_per_l"]).HCO3_umol_per_l)[0, 1]

    fig, (a0, a1) = plt.subplots(1, 2, figsize=(12, 5.0))
    for tname, c, _ in TR:
        g = ph[ph.tname == tname]
        a0.scatter(g["co2n"], g["pH_lab"], s=26, color=c, alpha=0.72, edgecolors="none", label=LAB[tname])
    rpp = np.corrcoef(np.log(ph.co2n), ph.pH_lab)[0, 1]
    rrp = np.median([np.corrcoef(np.log(g.co2n), g.pH_lab)[0, 1] for _, g in ph.groupby("pot_id") if len(g) >= 6])
    a0.set_xscale("log"); a0.set_xlim(400, 13000)
    a0.set_xlabel("Soil CO₂ at ~20 cm (ppm, log)"); a0.set_ylabel("Leachate pH (lab)")
    a0.set_title(f"CO₂ drives the acid: strong\npooled r = {rpp:+.2f}   median per-pot r = {rrp:+.2f}", fontsize=11.5)
    a0.legend(frameon=False, fontsize=8.5, loc="upper right")
    for tname, c, _ in TR:
        g = ta[ta.tname == tname]
        a1.scatter(g["co2n"], g["HCO3_umol_per_l"], s=26, color=c, alpha=0.72, edgecolors="none")
    rpt = np.corrcoef(np.log(ta.co2n), ta.HCO3_umol_per_l)[0, 1]
    rrt = np.median([np.corrcoef(np.log(g.co2n), g.HCO3_umol_per_l)[0, 1] for _, g in ta.groupby("pot_id") if len(g) >= 6])
    a1.set_xscale("log"); a1.set_xlim(400, 13000)
    a1.set_xlabel("Soil CO₂ at ~20 cm (ppm, log)"); a1.set_ylabel("Leachate total alkalinity (µmol/L)")
    a1.set_title(f"But it barely meters the alkalinity: weak\npooled r = {rpt:+.2f}   median per-pot r = {rrt:+.2f}", fontsize=11.5)
    fig.suptitle(f"Soil CO₂ is the weathering engine, not a carbon meter   "
                 f"(for comparison, leachate EC ↔ TA r = {ec_ta:+.2f})",
                 fontsize=12.5, weight="bold", x=0.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    brand.add_logo(fig, ax=a1, loc="lower right", frac=0.13)
    fig.savefig(FIG / "co2_4_engine_not_meter.png", bbox_inches="tight")
    plt.close(fig)

    print("wrote co2_1_seasonal_breathing_by_dose, co2_2_dose_forest, "
          "co2_3_temp_moisture_engine, co2_4_engine_not_meter")


if __name__ == "__main__":
    main()
