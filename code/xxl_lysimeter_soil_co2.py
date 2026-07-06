#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XXL Lysimeter — per-pot soil-CO2 story (one sensor in every pot, n=3-4 per dose).

Reads the living soil through the buried CO2 sensors: what the gas teaches us about
soil processes, and why the basalt dose barely changes any of it.

Inputs:
  output/soil_co2_by_pot_daily.csv    (daily CO2, one sensor per pot)
  Monitoring/soil_temperature_30cm.xlsx, soil_moisture_60cm.xlsx, soil_ec_60cm.xlsx
  output/xxl_lysimeter_data_wide.csv   (leachate pH / TA per pot)

Produces output/figures/:
  co2_1_seasonal_breathing_by_dose.png   seasonal cycle + doses converge
  co2_2_dose_forest.png                  season-adjusted CO2 vs control (n.s.)
  co2_3_temp_moisture_engine.png         warmth drives, drought throttles (LOWESS + CI)
  co2_4_engine_not_meter.png             CO2 -> leachate pH (strong) vs TA (weak)
  co2_5_birch_rewetting.png              repeated Birch effect: CO2 burst + EC flush
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


def _site_weekly(fn, pfx, lo, hi):
    m = pd.read_excel(MON / fn); m.columns = [str(c).strip() for c in m.columns]
    m["date"] = pd.to_datetime(m["Zeitstempel"], errors="coerce").dt.normalize()
    vc = [c for c in m.columns if c.startswith(pfx)]
    mm = m.melt("date", value_vars=vc, value_name="v").dropna(subset=["v"])
    mm["v"] = pd.to_numeric(mm["v"], errors="coerce")
    mm = mm[(mm.v >= lo) & (mm.v <= hi)]
    return mm.groupby("date")["v"].mean().sort_index()


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.ticker as mticker
    from statsmodels.nonparametric.smoothers_lowess import lowess
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 150, "font.size": 11,
                         "axes.grid": True, "grid.color": "#ededed",
                         "axes.spines.top": False, "axes.spines.right": False})
    import brand_standalone as brand
    FIG.mkdir(parents=True, exist_ok=True)
    co2 = load()

    # ================= FIGURE 1: seasonal breathing, doses overlaid =================
    fig, ax = plt.subplots(figsize=(11, 5.0))
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
    pot = pot.assign(ratio=np.exp(pot["resid"] - rc))
    order = ["Control", "100 t/ha", "200 t/ha", "400 t/ha", "FINE"]
    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    ax.axvline(1.0, color=OK["black"], lw=1.3, ls="--", zorder=1)
    for i, t in enumerate(reversed(order)):
        y = i
        sub = pot[pot.treatment == t]; c = COL[t]; n = len(sub)
        jit = np.linspace(-0.16, 0.16, n) if n > 1 else np.array([0.0])
        ax.scatter(sub["ratio"], y + jit, s=55, color=c, alpha=0.45, edgecolors="none", zorder=3)
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
                 "The pots scatter ×0.5–×1.7 within every treatment; means overlap control (400 t/ha ~18 % lower, n.s.)",
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
    moday = _site_weekly("soil_moisture_60cm.xlsx", "EC.60", 2.5, 60).rename("moist")

    w = pd.read_csv(OUT / "xxl_lysimeter_data_wide.csv", parse_dates=["date"])
    f = w[w.soil == "FUERTH2022"].copy()

    def to_potid(v):
        a, b = v.split(".")
        return ("FINE200." + b) if a == "FINE" else (a + "." + b)
    f["pot_id"] = f["variant"].map(lambda v: to_potid(v) if "." in v else v)

    def nearest(pot_id, dte, tol=12):
        s = co2[co2.pot_id == pot_id]
        if not len(s):
            return np.nan
        dd = (s.date - dte).abs().dt.days
        j = dd.values.argmin()
        return s.iloc[j]["soil_co2_ppm"] if dd.iloc[j] <= tol else np.nan
    _pref = {"000": "Control", "100": "100 t/ha", "200": "200 t/ha",
             "400": "400 t/ha", "FINE200": "FINE"}

    # ============ FIGURE 3: temp × moisture engine (LOWESS + bootstrap CI) ==========
    # Warmth drives respiration; drought throttles it. Moisture is not a clean function
    # of temperature (wet spring & dry autumn share a temperature), so we show a broad
    # LOWESS trend with a bootstrap CI band rather than per-bin medians.
    cc = co2.merge(tday, on="date").merge(moday, on="date")
    daily = pd.DataFrame({"co2": co2.groupby("date")["soil_co2_ppm"].median(),
                          "temp": tday, "moist": moday}).dropna()
    g0, g1 = daily.temp.quantile(.02), daily.temp.quantile(.98)
    grid = np.linspace(g0, g1, 140)

    def loess_ci(x, y, frac=0.5, B=400, seed=0):
        x = np.asarray(x, float); y = np.asarray(y, float); n = len(x)
        rng = np.random.default_rng(seed)
        fit = lambda xx, yy: np.interp(grid, *lowess(yy, xx, frac=frac, return_sorted=True).T)
        mean = fit(x, y)
        boot = np.array([fit(x[i], y[i]) for i in (rng.integers(0, n, n) for _ in range(B))])
        return mean, np.percentile(boot, 2.5, 0), np.percentile(boot, 97.5, 0)

    cm, cl, ch = loess_ci(daily.temp, np.log(daily.co2)); cm, cl, ch = np.exp(cm), np.exp(cl), np.exp(ch)
    mm_, ml, mh = loess_ci(daily.temp, daily.moist)
    r_lo = np.corrcoef(cc[cc.temp <= 18].temp, np.log(cc[cc.temp <= 18].soil_co2_ppm))[0, 1]
    r_hi = np.corrcoef(cc[cc.temp > 18].temp, np.log(cc[cc.temp > 18].soil_co2_ppm))[0, 1]
    fig, ax = plt.subplots(figsize=(10.6, 5.4))
    rng = np.random.default_rng(0)
    jt = cc["temp"].to_numpy() + rng.uniform(-0.8, 0.8, len(cc))
    ax.scatter(jt, cc["soil_co2_ppm"], s=8, color=OK["grey"], alpha=0.15, edgecolors="none",
               zorder=1, label="daily reading (one pot)")
    ax.fill_between(grid, cl, ch, color="#111111", alpha=0.20, lw=0, zorder=3)
    ax.plot(grid, cm, "-", color="#111111", lw=2.8, zorder=4, label="soil CO₂ (LOWESS ± 95 % CI)")
    ax.axvline(18, color=OK["verm"], ls="--", lw=1.6, zorder=2)
    ax.set_yscale("log"); ax.set_ylim(600, 20000)
    ax.set_xlabel("Soil temperature at 30 cm (°C), site mean")
    ax.set_ylabel("Soil CO₂ at ~20 cm (ppm, log)")
    twin = ax.twinx()
    twin.fill_between(grid, ml, mh, color=OK["blue"], alpha=0.16, lw=0, zorder=3)
    twin.plot(grid, mm_, "-", color=OK["blue"], lw=2.8, zorder=4, label="soil moisture (LOWESS ± 95 % CI)")
    twin.set_ylabel("Soil moisture at 60 cm (%)", color=OK["blue"])
    twin.tick_params(axis="y", colors=OK["blue"]); twin.set_ylim(18, 28); twin.grid(False)
    ax.set_title("Warm soil breathes more CO₂ — until it dries out\n"
                 f"CO₂ climbs with temperature (≤18 °C r = {r_lo:+.2f}) then reverses (>18 °C r = {r_hi:+.2f}) "
                 "as soil moisture declines", fontsize=12, loc="left")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = twin.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=9, loc="lower center")
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

    # ============ FIGURE 5: a repeated Birch effect (one drought-to-drought cycle) ==
    # Align soil CO2 (daily) and soil EC (weekly) at each deep dry->wet transition and run
    # each curve to the NEXT rewetting (marker v) — one full cycle per event. The 2025 event
    # has no CO2 (sensors gone) but still shows in EC.
    ec = _site_weekly("soil_ec_60cm.xlsx", "EC.60", 1, 2000)
    mser = moday.sort_index(); mv = mser.values; md = mser.index
    evs = []
    for i in range(1, len(mv) - 1):                       # all deep moisture minima that rewet
        if mv[i] <= mv[i - 1] and mv[i] < mv[i + 1] and mv[i] < 16:
            fwd = mser[(md > md[i]) & (md <= md[i] + pd.Timedelta(days=28))]
            if len(fwd) and fwd.max() - mv[i] >= 6:
                evs.append((md[i], float(mv[i])))
    pr = []                                               # prune events closer than 30 days
    for e in sorted(evs):
        if pr and (e[0] - pr[-1][0]).days < 30:
            if e[1] < pr[-1][1]:
                pr[-1] = e
        else:
            pr.append(e)
    ecolors = [OK["orange"], OK["verm"], OK["blue"], OK["green"], OK["purple"]]
    tmax = ec.index.max()                                 # last event runs to the data end
    smooth = lambda s: s.rolling(11, center=True, min_periods=3).mean()

    def _tmin_rel(t0, W1):                                # winter temperature minimum -> spring
        w = tday[(tday.index >= t0) & (tday.index <= t0 + pd.Timedelta(days=W1))]
        return int((w.idxmin() - t0).days) if len(w) >= 5 else None

    def _split(ax, x, y, c, sp, lw):                     # solid to sp, dashed after (next warm season)
        x = np.asarray(x, float); y = np.asarray(y, float)
        if sp is None:
            ax.plot(x, y, "-", color=c, lw=lw); return
        s = x <= sp
        ax.plot(x[s], y[s], "-", color=c, lw=lw)
        d = x >= sp
        if d.sum() > 1:
            ax.plot(x[d], y[d], "--", color=c, lw=lw, alpha=0.85)

    fig, (b0, b1) = plt.subplots(1, 2, figsize=(14.5, 5.4))
    for k, (t0, mn) in enumerate(pr):
        c = ecolors[k % len(ecolors)]
        W1 = (pr[k + 1][0] - t0).days if k + 1 < len(pr) else (tmax - t0).days
        sp = _tmin_rel(t0, W1)
        post = tday[(tday.index >= t0) & (tday.index <= t0 + pd.Timedelta(days=14))].mean()
        sub = co2[(co2.date >= t0 - pd.Timedelta(days=42)) & (co2.date <= t0 + pd.Timedelta(days=W1))].copy()
        sub["rel"] = (sub.date - t0).dt.days
        has_co2 = int(sub["rel"].between(0, 42).sum()) > 10
        lab = f"{t0.strftime('%Y-%m')}: {mn:.0f}% dry, {post:.0f}°C after" + ("" if has_co2 else "  (EC only)")
        if has_co2:
            g = sub.groupby("rel")["soil_co2_ppm"]
            med = smooth(g.median()).dropna()
            b0.fill_between(g.median().index, smooth(g.quantile(.25)).values,
                            smooth(g.quantile(.75)).values, color=c, alpha=0.10, lw=0)
            _split(b0, med.index, med.values, c, sp, 2.4)
            if len(med):
                b0.plot(med.index[-1], med.values[-1], "v", color=c, ms=10, zorder=7)
            b0.plot([], [], "-", color=c, label=lab)
        we = ec[(ec.index >= t0 - pd.Timedelta(days=42)) & (ec.index <= t0 + pd.Timedelta(days=W1))]
        rel = (we.index - t0).days
        _split(b1, rel, we.values, c, sp, 2.0)           # no markers so the dashes are visible
        if len(we):
            b1.plot(rel[-1], we.values[-1], "v", color=c, ms=10, zorder=7)
        b1.plot([], [], "-", color=c, label=lab)
    for ax in (b0, b1):
        ax.axvline(0, color="#444", ls="--", lw=1.4)
        ax.axvspan(-42, 0, color=OK["grey"], alpha=0.07, lw=0)
        for x in (90, 180, 270):
            ax.axvline(x, color="#ededed", lw=1, zorder=0)
    b0.plot([], [], "-", color="#555", label="solid: this event’s response")
    b0.plot([], [], "--", color="#555", label="dashed: next warm season")
    b0.set_ylim(0, 10000)
    b0.set_ylabel("Soil CO₂ (ppm) — median + IQR across pots")
    b0.set_xlabel("days from rewetting (soil-moisture minimum)")
    b0.set_title("CO₂: one drought-to-drought cycle  (▼ = next rewetting; dashed = next warm season)")
    b0.legend(frameon=False, fontsize=7.5, loc="upper right")
    b1.set_ylabel("Soil EC at 60 cm (µS/cm), weekly")
    b1.set_xlabel("days from rewetting (soil-moisture minimum)")
    b1.set_title("Salt flush: EC rises on every rewetting  (▼ = next rewetting)")
    b1.legend(frameon=False, fontsize=7.5, loc="upper right")
    fig.suptitle("A repeated Birch effect: each rewetting shapes the whole cycle until the next drought "
                 "— CO₂ burst (when warm) and EC salt flush (every time)",
                 fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    brand.add_logo(fig, ax=b1, loc="lower right", frac=0.12)
    fig.savefig(FIG / "co2_5_birch_rewetting.png", bbox_inches="tight")
    plt.close(fig)

    print("wrote co2_1_seasonal_breathing_by_dose, co2_2_dose_forest, "
          "co2_3_temp_moisture_engine, co2_4_engine_not_meter, co2_5_birch_rewetting")


if __name__ == "__main__":
    main()
