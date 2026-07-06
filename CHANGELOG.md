# Changelog — XXL Lysimeter Experiment (Fürth 2022) dataset

Public releases of the Fürth-2022 dataset. Newest first.

---

## v1.4 — 2026-07-06 — Dryness filter removed; figures pruned; instrumentation documented
- **IMPACT — no dryness filter on EC/pH.** The monitoring code no longer drops readings below
  10 % VWC (the LSE01 shares prongs for EC/moisture and compensates EC internally, so moisture is
  not an independent variable). Pooled 60 cm soil-EC ↔ leachate EC **0.71 → 0.70** (n 353 → 355),
  TA 0.46 → 0.45; the monitoring correlation CSVs, weekly sensor exports and `story_1` /
  `monitoring_soilEC_*` figures were regenerated. **No TA/flux values changed.**
- **`figures/` pruned 29 → 19:** removed 10 PNGs referenced by neither the articles nor this
  README (retired `story_5`/`story_2b`, old `monitoring_leachate_sensor_correlation*` pair,
  `ph_histogram`, unused `alt_FUERTH2022_*` variants).
- **`co2_1_seasonal_breathing_by_dose.png`** rebuilt with a 30-day rolling median (smoother) and a
  higher y-axis so summer peaks are not clipped.
- **README:** added an **Instrumentation (hardware)** table (Dragino LSE01/LSPH01, Seeed soil-CO₂
  + SenseCAP S2103, Milesight EM500-CO2; gauges/gateway/cameras TBC); removed blog-series
  references and the stale dryness-filter note; removed the defunct Wunderground mention.

## v1.3 — 2026-07-06 — Soil-CO₂ survivorship corrected
- **IMPACT — `data/monitoring_sensor_survivorship.csv` and
  `figures/monitoring_sensor_survivorship.png` corrected.** The soil-CO₂ channel now counts the
  **20 per-pot sensors** (`data/soil_co2_by_pot_daily.csv`) instead of the legacy 4-channel
  source. Column header `soil_co2 (of 4)` → `soil_co2 (of 20)`; the CO₂ curve now peaks at 20
  (Oct 2022) and falls to a single survivor by early 2025. **No leachate/TA/flux values changed.**

## v1.2 — 2026-07-05 — Educational article 5; a repeated Birch effect
- Added `figures/co2_5_birch_rewetting.png`: aligning daily soil CO₂ at each deep dry→wet
  transition reveals a **repeated Birch effect** — a respiration burst on rewetting (large in
  summer, weak in cool autumn) and a soil-EC salt flush after every event.
- Upgraded the engine figure to a LOWESS + bootstrap-CI band (`co2_3_temp_moisture_engine.png`);
  removed the binned `co2_3b` variant. `code/xxl_lysimeter_soil_co2.py` emits `co2_1..5`.
  Article 5 retitled/reframed as educational. **No data values changed.**

## v1.1 — 2026-07-05 — Per-pot soil CO₂ added; article 5 becomes a deep dive

- **New data: a soil-CO₂ sensor in every pot.** Added `data/soil_co2_by_pot_daily.csv` (daily
  ~20 cm CO₂ for all **20 pots**, n = 4 per dose — not one per treatment as previously stated),
  with raw exports in `monitoring/soil_co2_by_pot_raw/`; the "MIXED" export is a fourth FINE
  pot, included as `FINE200.MIXED`. Cleaning: 0, sub-400 ppm (below atmospheric)
  and >40,000 ppm removed; control de-duplicated across the treatment exports on sensor + date.
- **New analysis + figures** (`code/xxl_lysimeter_soil_co2.py`): `co2_1_seasonal_breathing_by_dose`,
  `co2_2_dose_forest`, `co2_3_temp_moisture_engine`, `co2_4_engine_not_meter`.
- **Findings.** Even with n = 4/dose, no significant dose effect on soil CO₂ (400 t/ha ~18 % low,
  p = 0.33). Soil CO₂ drives leachate acidity (pH r = −0.68) but meters alkalinity only weakly
  (TA r = +0.36 vs EC ↔ TA +0.63) — engine, not meter. CO₂ rises with temperature then reverses
  above ~18 °C as the soil dries (temperature × moisture limit). Mechanism chain confirmed
  per-pot. Removed the retired `story_5` framing from §7; article 5 retitled to the deep dive.

## v1.0.1 — 2026-07-05 — Buried-EC finding reworded

- Clarified the buried-EC result: soil-EC and soil moisture are read from the same Dragino
  LSE01 prongs, so moisture is **not an independent confounder** of the EC reading. Removed
  the moisture-controlled correlation uplift and `figures/story_4_moisture_confounder.png`.
  The headline is now the raw 60 cm soil-EC ↔ leachate EC r ≈ 0.71 (Ca/Mg ≈ 0.70, TA ≈ 0.46;
  30 cm r ≈ 0.39), which is unchanged by the 10 % dryness filter (only 3/355 leachate-paired
  readings are dry). **No data values changed.**

## v1.0 — 2026-07-04 — First public release

- First open release of the **XXL Lysimeter Experiment**, soil **"Fürth 2022"**: leachate
  chemistry and cumulative bicarbonate export (local CDR), buried soil-sensor time series,
  on-site and official weather, and feedstock characterization. Companion to the two-year
  greenhouse dataset.
- **Scope: Fürth-2022 experiment only.** A 2025 follow-on experiment (most pots repurposed
  with a new soil and new feedstocks) is intentionally excluded and will be released
  separately.
- **Sensor provenance after the 2025 changeover:** only the five continuing Fürth-2022 pots
  (`000.A`, `100.A`, `200.A`, `400.A`, `400.E`) are retained in the soil-sensor products
  after `2025-05-15`; readings from the repurposed pots are removed. Soil temperature is
  site-level and could not be pot-attributed, so it ends at `2025-05-15`; soil CO₂ (four
  continuing A-pots) and the other sensors (EC, pH, moisture, continuing pots) run to the
  end of 2025.
- Provenance: surface area **0.406 m²/pot**; CO₂ factor **1 mol CO₂ / mol HCO₃⁻**; leachate
  volume default model **`avgBD`** (best by out-of-sample plausibility check). Pipeline
  validated against the original project notebook (median relative error ≈ 0).
- **Absolute CDR is gross export, not input-corrected:** it does not subtract the alkalinity
  brought in by irrigation. In 2022 each pot got ~111 L hard tap water (Infra Fürth, 16.7 °dGH,
  ≈ 5.1 mmol/L HCO₃⁻) of order 0.5 tCO₂e/ha (up to ~0.6 mass-balance ceiling) ≈ a third of
  gross, so absolute CDR is an upper bound (irrigation-corrected ≈ 1.0–1.1 tCO₂e/ha).
  Common-mode across pots → treatment-vs-control
  comparisons unaffected. First ~90 days = initial flush / Birch effect. See README §5.
- Figures branded with the Carbon Drawdown Initiative logo. Includes two irrigation-blank
  figures (`water_irrigation_share_2022.png`, `TA_cumulative_gross_vs_net_tapwater.png`) and
  the script that makes them (`code/xxl_lysimeter_water_share.py`).
- Released under **CC-BY-4.0**.
