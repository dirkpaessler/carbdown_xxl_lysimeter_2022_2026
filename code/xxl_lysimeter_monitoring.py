#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XXL Lysimeter — in-situ soil sensor analysis (secondary to the main pipeline).

Reads the raw sensor exports in ``Monitoring/`` (soil moisture, temperature, EC and
pH at 30/60 cm, soil/tank/ambient CO2) and the leachate table produced by
``xxl_lysimeter_pipeline.py`` (``output/xxl_lysimeter_data_wide.csv``). Cleans the
sensor data (plausibility filters — many sensors died / batteries ran out), then:

  1. Plots the in-situ soil EC sensor vs. the leachate EC, split by treatment
     ("variation") and by depth (30 / 60 cm), with per-panel correlation.
  2. Computes how strongly every leachate variable correlates with every sensor,
     **pot-wise** (each pot's own sensor paired with its own leachate) and pooled
     per treatment — as a heatmap + a ranked table.
  3. Writes cleaned site-mean and pot-level sensor tables for downstream use.

Run after the main pipeline:  python3 xxl_lysimeter_monitoring.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MON = HERE / "Monitoring"
OUT = HERE / "output"
FIG = OUT / "figures"


def _brand(fig, loc="lower right", frac=0.10, pad=0.008):
    """Stamp the Carbon-Drawdown logo in the OUTER figure margin (never over data).

    These monitoring figures are dense (heatmaps, sensor grids) with no empty
    interior corner, so we place the logo in a full-figure frame's corner = the
    figure margin. Never raises."""
    try:
        import brand_standalone as brand
        frame = fig.add_axes([0, 0, 1, 1], zorder=9990)
        frame.axis("off"); frame.set_facecolor("none")
        return brand.add_logo(fig, ax=frame, loc=loc, frac=frac, pad=pad)
    except Exception:
        return None

# Sensor files and plausibility bounds (values outside -> dropped).
SENSORS = {
    "soil_moisture_30cm_pct": ("soil_moisture_30cm.xlsx", "EC.30", None, 2.5, None),
    "soil_moisture_60cm_pct": ("soil_moisture_60cm.xlsx", "EC.60", None, 2.5, None),
    "soil_temp_30cm_C":       ("soil_temperature_30cm.xlsx", None, ["temp_SOIL"], -5, 50),
    "soil_ec_30cm":           ("soil_ec_30cm.xlsx", "EC.30", None, 1, 2000),
    "soil_ec_60cm":           ("soil_ec_60cm.xlsx", "EC.60", None, 1, 2000),
    "soil_ph_30cm":           ("soil_ph_30cm.xlsx", "pH.30", None, 3, 12),
    "soil_ph_60cm":           ("soil_ph_60cm.xlsx", "pH.60", None, 3, 12),
}
# Below this volumetric water content the bulk-EC and pH sensors lose reliable
# contact with pore water (EC collapses ~3-10x); such readings are dropped.
DRY_THRESHOLD_VWC = 10.0

CO2_FILE = "co2_concentrations.xlsx"
CO2_GROUPS = {
    "soil_co2_ppm": (["SoilCO2.000.A", "SoilCO2.100.A", "SoilCO2.200.A", "SoilCO2.400.A"], 1, 40000),
    "tank_air_co2_ppm": (["Tank-Air-CO2.000.A", "Tank-Air-CO2.200.A", "Tank-Air-CO2.400.A"], 1, 10000),
    "ambient_co2_ppm": (["XXL Lysimeters Ambient CO2 (20 cm)"], 100, 2000),
}

LEACHATE_PARAMS = {
    "HCO3_umol_per_l": "TA (HCO₃)", "EC_lab_uS_per_cm_25degC": "EC (lab)",
    "EC_field_uS_per_cm_25degC": "EC (field)", "Ca_umol_per_l": "Ca",
    "Mg_umol_per_l": "Mg", "sum_cations_meq_per_l": "Σcations",
    "pH_field": "pH", "Si_umol_per_l": "Si", "Na_umol_per_l": "Na",
}


def _sensor_pot(col: str) -> str | None:
    """Map a sensor column to a canonical pot id (000.A … 400.E)."""
    m = re.search(r"\((?:was|aka)\s*(\d{3}\.[A-E])\)", col)   # "FINE-200.A (was 000.E)"
    if m:
        return m.group(1)
    m = re.search(r"(\d{3}\.[A-E])", col)                      # "EC.30.100.A"
    return m.group(1) if m else None


def _read_long(fname, prefix=None, valcols=None, lo=None, hi=None) -> pd.DataFrame:
    """Read one sensor file to long format (date, pot, value), plausibility-filtered."""
    df = pd.read_excel(MON / fname)
    df.columns = [str(c).strip() for c in df.columns]
    df["date"] = pd.to_datetime(df["Zeitstempel"], errors="coerce").dt.normalize()
    cols = valcols or [c for c in df.columns if c.startswith(prefix)]
    m = df.melt("date", value_vars=cols, var_name="col", value_name="v").dropna(subset=["v"])
    m["v"] = pd.to_numeric(m["v"], errors="coerce")
    if lo is not None:
        m = m[m["v"] >= lo]
    if hi is not None:
        m = m[m["v"] <= hi]
    if valcols == ["temp_SOIL"]:
        # temp file has one value column; pot is in 'Entity Name' — not mapped here,
        # so this branch is only used for the site mean (pot=None).
        m["pot"] = None
    else:
        m["pot"] = m["col"].map(_sensor_pot)
    return m[["date", "pot", "v"]]


def load_sensors_pot_level(variants):
    """Per-pot daily sensor values for the depth-resolved sensors (EC, pH, moisture)."""
    frames = {}
    for name, (fname, prefix, valcols, lo, hi) in SENSORS.items():
        if name == "soil_temp_30cm_C":
            continue                      # temp file is per-Entity, handled as site mean only
        d = _read_long(fname, prefix, valcols, lo, hi).dropna(subset=["pot"])
        d = d.groupby(["date", "pot"], as_index=False)["v"].mean().rename(columns={"v": name})
        frames[name] = d
    # merge all per-pot sensors on (date, pot)
    out = None
    for name, d in frames.items():
        out = d if out is None else out.merge(d, on=["date", "pot"], how="outer")
    # Confounder: mask EC/pH readings taken in soil too dry for the sensor to work.
    for depth in ("30cm", "60cm"):
        sm = f"soil_moisture_{depth}_pct"
        if sm not in out:
            continue
        dry = out[sm] < DRY_THRESHOLD_VWC
        for q in (f"soil_ec_{depth}", f"soil_ph_{depth}"):
            if q in out:
                out.loc[dry, q] = np.nan
    return out.sort_values(["pot", "date"]).reset_index(drop=True)


def _partial_corr(df, x, y, z):
    """Partial Pearson r of x,y controlling for z (all same rows)."""
    g = df.dropna(subset=[x, y, z])
    if len(g) < 8:
        return np.nan, len(g)
    rxy = np.corrcoef(g[x], g[y])[0, 1]
    rxz = np.corrcoef(g[x], g[z])[0, 1]
    ryz = np.corrcoef(g[y], g[z])[0, 1]
    denom = np.sqrt((1 - rxz**2) * (1 - ryz**2))
    return ((rxy - rxz * ryz) / denom if denom else np.nan), len(g)


def load_sensor_sitemeans():
    """Site-mean daily series for every sensor (incl. temp + CO2)."""
    cols = {}
    for name, (fname, prefix, valcols, lo, hi) in SENSORS.items():
        if name == "soil_temp_30cm_C":
            df = pd.read_excel(MON / fname); df.columns = [str(c).strip() for c in df.columns]
            df["date"] = pd.to_datetime(df["Zeitstempel"], errors="coerce").dt.normalize()
            v = pd.to_numeric(df["temp_SOIL"], errors="coerce")
            v = v[(v >= lo) & (v <= hi)]
            cols[name] = v.groupby(df["date"]).mean()
        else:
            d = _read_long(fname, prefix, valcols, lo, hi)
            cols[name] = d.groupby("date")["v"].mean()
    df = pd.read_excel(MON / CO2_FILE); df.columns = [str(c).strip() for c in df.columns]
    df["date"] = pd.to_datetime(df["Zeitstempel"], errors="coerce").dt.normalize()
    for name, (chans, lo, hi) in CO2_GROUPS.items():
        m = df.melt("date", value_vars=chans, value_name="v").dropna(subset=["v"])
        m["v"] = pd.to_numeric(m["v"], errors="coerce")
        m = m[(m["v"] >= lo) & (m["v"] <= hi)]
        cols[name] = m.groupby("date")["v"].mean()
    S = pd.DataFrame(cols).sort_index()
    S.index.name = "date"
    return S


def sensor_survivorship(plt):
    """Count active channels over time per sensor type (age/attrition) + figure/CSV."""
    specs = [(n, f, p, v, lo, hi) for n, (f, p, v, lo, hi) in SENSORS.items()
             if n != "soil_temp_30cm_C"]
    counts = {}
    for name, fname, prefix, valcols, lo, hi in specs:
        df = pd.read_excel(MON / fname); df.columns = [str(c).strip() for c in df.columns]
        df["q"] = pd.to_datetime(df["Zeitstempel"], errors="coerce").dt.to_period("M")
        cols = valcols or [c for c in df.columns if c.startswith(prefix)]
        m = df.melt("q", value_vars=cols, var_name="ch", value_name="v").dropna(subset=["v"])
        m["v"] = pd.to_numeric(m["v"], errors="coerce")
        m = m[(m["v"] >= lo) & (m["v"] <= (hi if hi else 1e12))]
        counts[f"{name} (of {len(cols)})"] = m.groupby("q")["ch"].nunique()
    # CO2 soil sensors
    df = pd.read_excel(MON / CO2_FILE); df.columns = [str(c).strip() for c in df.columns]
    df["q"] = pd.to_datetime(df["Zeitstempel"], errors="coerce").dt.to_period("M")
    chans = ["SoilCO2.000.A", "SoilCO2.100.A", "SoilCO2.200.A", "SoilCO2.400.A"]
    m = df.melt("q", value_vars=chans, var_name="ch", value_name="v").dropna(subset=["v"])
    m["v"] = pd.to_numeric(m["v"], errors="coerce"); m = m[(m["v"] >= 1) & (m["v"] <= 40000)]
    counts["soil_co2 (of 4)"] = m.groupby("q")["ch"].nunique()
    surv = pd.DataFrame(counts)
    surv.index = surv.index.to_timestamp()
    surv.to_csv(OUT / "monitoring_sensor_survivorship.csv")
    fig, ax = plt.subplots(figsize=(11, 4.8))
    for c in surv.columns:
        ax.plot(surv.index, surv[c], "-o", ms=3, lw=1.4, label=c)
    ax.set_ylabel("active sensors (channels reporting valid data)")
    ax.set_xlabel("Date")
    ax.set_title("XXL Lysimeter — sensor survivorship (age/attrition confounder)")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.text(0.5, 0.005, "Many sensors die over time (battery/failure). Late-period SITE "
             "MEANS rest on few surviving sensors → less representative. Pot-wise "
             "correlations are unaffected (each pot paired with its own sensor).",
             ha="center", fontsize=7.5, color="#666")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _brand(fig, loc="lower right", frac=0.10)
    p = FIG / "monitoring_sensor_survivorship.png"
    fig.savefig(p, dpi=140); plt.close(fig)
    return p


def _nearest(series: pd.Series, target, tol_days=7):
    s = series.dropna()
    if s.empty:
        return np.nan
    dd = np.abs((s.index - target).days)
    j = int(dd.argmin())
    return s.iloc[j] if dd[j] <= tol_days else np.nan


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 120, "axes.grid": True, "grid.color": "#e6e6e6",
                         "axes.spines.top": False, "axes.spines.right": False})
    FIG.mkdir(parents=True, exist_ok=True)

    vpath = HERE / "Lysimeter Fürth" / "variants.json"
    variants = json.loads(vpath.read_text())
    tr_of = {v: d["treatment"] for v, d in variants["variants"].items()}
    TSTYLE = {"000": ("#333333", "Control"), "100": ("#56B4E9", "100 t/ha"),
              "200": ("#0072B2", "200 t/ha"), "400": ("#D55E00", "400 t/ha"),
              "FINE": ("#009E73", "200 t/ha fine")}

    wide = pd.read_csv(OUT / "xxl_lysimeter_data_wide.csv", parse_dates=["date"])
    old = wide[wide["soil"] == "FUERTH2022"].copy()

    pot_sensors = load_sensors_pot_level(variants)
    site = load_sensor_sitemeans()
    MON.mkdir(exist_ok=True)
    site.to_csv(MON / "sensor_sitemean_weekly.csv")
    pot_sensors.to_csv(MON / "sensor_potlevel_weekly.csv", index=False)

    # ---- pair each leachate (pot,date) with that pot's nearest sensor reading -----
    rows = []
    for _, r in old.iterrows():
        pot, d = r["variant"], r["date"]
        rec = {"variant": pot, "treatment": r["treatment"], "date": d}
        for c in LEACHATE_PARAMS:
            rec[c] = r.get(c)
        ps = pot_sensors[pot_sensors["pot"] == pot]
        for sc in [c for c in pot_sensors.columns if c not in ("date", "pot")]:
            rec[sc] = _nearest(ps.set_index("date")[sc], d) if not ps.empty else np.nan
        # CO2 only exists for A-pots; use site mean as proxy context
        for sc in ("soil_co2_ppm", "tank_air_co2_ppm"):
            rec[sc] = _nearest(site[sc], d)
        rec["soil_temp_30cm_C"] = _nearest(site["soil_temp_30cm_C"], d)
        rows.append(rec)
    paired = pd.DataFrame(rows)
    paired.to_csv(OUT / "monitoring_leachate_sensor_paired.csv", index=False)

    # ============ FIGURE 1: soil EC sensor vs leachate EC, treatment × depth ======
    treatments = [t for t in ["000", "100", "200", "400", "FINE"]
                  if t in set(paired["treatment"])]
    depths = [("soil_ec_30cm", "30 cm"), ("soil_ec_60cm", "60 cm")]
    fig, axes = plt.subplots(len(treatments), len(depths),
                             figsize=(4.2 * len(depths), 2.7 * len(treatments)),
                             squeeze=False)
    lea_ec = "EC_lab_uS_per_cm_25degC"
    for i, tr in enumerate(treatments):
        col, lab = TSTYLE[tr]
        sub = paired[paired["treatment"] == tr]
        for j, (sc, dlab) in enumerate(depths):
            ax = axes[i][j]
            g = sub.dropna(subset=[lea_ec, sc])
            ax.scatter(g[lea_ec], g[sc], s=18, color=col, alpha=0.6, edgecolors="none")
            if len(g) >= 4:
                r = np.corrcoef(g[lea_ec], g[sc])[0, 1]
                b1, b0 = np.polyfit(g[lea_ec], g[sc], 1)
                xs = np.array([g[lea_ec].min(), g[lea_ec].max()])
                ax.plot(xs, b0 + b1 * xs, "-", color=col, lw=1.4)
                ax.text(0.04, 0.9, f"r={r:+.2f}  n={len(g)}", transform=ax.transAxes,
                        fontsize=8, va="top")
            if j == 0:
                ax.set_ylabel(f"{lab}\nsoil EC sensor")
            if i == len(treatments) - 1:
                ax.set_xlabel("Leachate EC (µS/cm)")
            if i == 0:
                ax.set_title(f"soil EC at {dlab}", fontsize=10)
    fig.suptitle("XXL Lysimeter — in-situ soil EC sensor vs. leachate EC "
                 "(by treatment × depth, old Fürth pots)", fontsize=12, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    _brand(fig, loc="lower right", frac=0.08)
    p1 = FIG / "monitoring_soilEC_vs_leachateEC_by_treatment_depth.png"
    fig.savefig(p1, bbox_inches="tight"); plt.close(fig)

    # ============ FIGURE 2: pot-wise correlation heatmap (leachate × sensor) ======
    sensor_cols = [c for c in paired.columns
                   if c not in list(LEACHATE_PARAMS) + ["variant", "treatment", "date"]]
    cormat = pd.DataFrame(index=list(LEACHATE_PARAMS.values()), columns=sensor_cols, dtype=float)
    nmat = cormat.copy()
    for lp, lab in LEACHATE_PARAMS.items():
        for sc in sensor_cols:
            g = paired.dropna(subset=[lp, sc])
            cormat.loc[lab, sc] = np.corrcoef(g[lp], g[sc])[0, 1] if len(g) >= 6 else np.nan
            nmat.loc[lab, sc] = len(g)
    cormat.to_csv(OUT / "monitoring_leachate_sensor_correlation_potwise.csv")
    fig, ax = plt.subplots(figsize=(1.1 * len(sensor_cols) + 3, 0.6 * len(cormat) + 2))
    cmap = plt.get_cmap("RdBu_r").copy(); cmap.set_bad("#dddddd")
    im = ax.imshow(np.ma.masked_invalid(cormat.values.astype(float)),
                   cmap=cmap, vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(sensor_cols))); ax.set_xticklabels(sensor_cols, rotation=40, ha="right", fontsize=8)
    ax.set_yticks(range(len(cormat))); ax.set_yticklabels(cormat.index, fontsize=9)
    for i in range(cormat.shape[0]):
        for j in range(cormat.shape[1]):
            v = cormat.values[i, j]
            if pd.notna(v):
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=7.2,
                        color="white" if abs(v) > 0.55 else "#222")
    fig.colorbar(im, fraction=0.02, pad=0.02).set_label("Pearson r", fontsize=8)
    ax.set_title("XXL Lysimeter — leachate vs. in-situ sensors, POT-WISE "
                 "(each pot's own sensor; pooled, old Fürth pots)", fontsize=11)
    fig.text(0.5, 0.005, f"Soil EC/pH dryness-filtered (moisture ≥ {DRY_THRESHOLD_VWC:.0f}% VWC). "
             "Controlling for moisture (partial r) keeps soil-EC↔leachate-EC even stronger — "
             "see monitoring_partialcorr_moisture_controlled.csv. Grey = too few points.",
             ha="center", fontsize=7.3, color="#666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    _brand(fig, loc="lower right", frac=0.10)
    p2 = FIG / "monitoring_leachate_sensor_correlation_potwise.png"
    fig.savefig(p2, bbox_inches="tight"); plt.close(fig)

    # ---- ranked "who talks to whom" ------------------------------------------
    long = cormat.stack().reset_index()
    long.columns = ["leachate", "sensor", "r"]
    long["abs_r"] = long["r"].abs()
    long = long.sort_values("abs_r", ascending=False)
    long.to_csv(OUT / "monitoring_correlation_ranked.csv", index=False)
    print("Top correlations (pot-wise, EC/pH dryness-filtered):")
    for _, r in long.head(12).iterrows():
        print(f"  {r['leachate']:12s} ↔ {r['sensor']:22s}  r={r['r']:+.2f}")

    # ---- partial correlations: EC/pH sensors controlled for soil moisture ----
    conf = {"soil_ec_30cm": "soil_moisture_30cm_pct", "soil_ec_60cm": "soil_moisture_60cm_pct",
            "soil_ph_30cm": "soil_moisture_30cm_pct", "soil_ph_60cm": "soil_moisture_60cm_pct"}
    pc_rows = []
    for lp, lab in LEACHATE_PARAMS.items():
        for sc, mc in conf.items():
            if sc in paired and mc in paired:
                raw = paired.dropna(subset=[lp, sc])
                r_raw = np.corrcoef(raw[lp], raw[sc])[0, 1] if len(raw) >= 6 else np.nan
                r_par, n = _partial_corr(paired, lp, sc, mc)
                pc_rows.append(dict(leachate=lab, sensor=sc, r_raw=r_raw,
                                    r_partial_moisture=r_par, n=n))
    pc = pd.DataFrame(pc_rows)
    pc.to_csv(OUT / "monitoring_partialcorr_moisture_controlled.csv", index=False)
    print("\nMoisture as confounder — leachate EC ↔ soil-EC, raw vs partial (control moisture):")
    for _, r in pc[pc["sensor"].isin(["soil_ec_30cm", "soil_ec_60cm"])].iterrows():
        if r["leachate"] in ("EC (lab)", "Σcations"):
            print(f"  {r['leachate']:10s} ↔ {r['sensor']:12s}  raw={r['r_raw']:+.2f}  "
                  f"partial={r['r_partial_moisture']:+.2f}  (n={int(r['n'])})")
    # ---- age confounder: (a) survivorship, (b) time-detrended correlations -----
    p3 = sensor_survivorship(plt)
    paired["days"] = (paired["date"] - paired["date"].min()).dt.days
    print("\nAge/time confounder — sensor↔leachate, raw vs partial|time (age trend removed):")
    checks = [("soil_ec_60cm", "EC (lab)"), ("soil_ec_30cm", "EC (lab)"),
              ("soil_temp_30cm_C", "pH"), ("soil_co2_ppm", "pH"), ("soil_ph_30cm", "EC (lab)")]
    lp_col = {v: k for k, v in LEACHATE_PARAMS.items()}
    for sc, lp in checks:
        col = lp_col[lp]
        g = paired.dropna(subset=[col, sc])
        r_raw = np.corrcoef(g[col], g[sc])[0, 1] if len(g) >= 10 else np.nan
        r_par, n = _partial_corr(paired, col, sc, "days")
        note = "  (was a time-trend artefact)" if abs(r_par) < abs(r_raw) - 0.15 else ""
        print(f"  {sc:20s} ↔ {lp:9s}  raw={r_raw:+.2f}  partial|time={r_par:+.2f}{note}")
    print(f"\nfigures: {p1.name}, {p2.name}, {p3.name}")
    return p1, p2, p3


if __name__ == "__main__":
    main()
