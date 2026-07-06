# XXL Lysimeter Experiment (1400 days) — Fürth 2022-2026 (Carbon Drawdown Initiative)

**Open dataset for our long-running enhanced-weathering lysimeter experiment**, soil
"Fürth 2022", 2022-05 … 2026 (~1,400 days). This is the data, code and figures for our
long-running, in-situ-instrumented XXL Lysimeter enhanced-weathering experiment — the
field companion to our two-year greenhouse study.

*Version 1.0 · 2026-07 · Experiment conducted by Carbon Drawdown Initiative,
www.carbon-drawdown.de · Contact: Dirk Paessler, info@carbon-drawdown.de*

---

## 1. What this experiment is

Enhanced rock weathering (EW) mixes reactive silicate or carbonate minerals into soil so
that their accelerated dissolution converts atmospheric CO₂ into dissolved bicarbonate.
The **XXL Lysimeter** measures that process outdoors, over years, in twenty large
lysimeter pots at our Fürth site.

- **Twenty pots**, each **0.406 m²** surface (0.70 × 0.58 m), filled in spring 2022 with a
  single soil (**"Fürth 2022"**) and planted.
- **Five treatments, four replicate pots each:** control (`000`, no rock), basalt at
  `100`/`200`/`400` t/ha, and `FINE` (200 t/ha fine grind — the four E-pots).
- Rain and irrigation percolate through; roughly **monthly** we pump and analyse the
  leachate (*Sickerwasser*) for **total alkalinity (TA, as HCO₃⁻)** — our CO₂-drawdown
  proxy — plus major ions, pH and electrical conductivity.
- Each instrumented pot carries **buried sensors** for soil moisture, temperature,
  electrical conductivity (EC) and pH at 30 and 60 cm; **every pot** also carries a
  **soil-CO₂** sensor at ~20 cm (20 in all). On-site rain gauges and ambient-CO₂ sensors
  complete the picture.

The headline quantity is the **cumulative CO₂-equivalent export** in t CO₂/ha, computed
from measured bicarbonate export.

### Instrumentation (hardware)

All buried and ambient sensors report over **LoRaWAN**. Per-pot channels are logged
sub-hourly and aggregated (weekly for the soil EC/pH/moisture series, daily for soil CO₂).

| Measurement | Device | Manufacturer |
| --- | --- | --- |
| Soil moisture, bulk EC & temperature (30 & 60 cm) | [LSE01](https://www.dragino.com/products/lora-lorawan-end-node/item/159-lse01.html) (LoRaWAN Soil Moisture & EC) | Dragino |
| Soil pH (30 & 60 cm) | [LSPH01](https://www.dragino.com/products/agriculture-weather-station/item/184-lsph01.html) (LoRaWAN Soil pH) | Dragino |
| Soil CO₂ (~20 cm, one per pot) | [LoRaWAN CO₂ Sensor, EU868](https://www.seeedstudio.com/LoRaWAN-CO2-Sensor-EU868-p-4311.html) | Seeed Studio |
| Ambient CO₂ + T/RH (20 cm and 200 cm) | [SenseCAP S2103](https://www.seeedstudio.com/SenseCAP-S2103-LoRaWAN-CO2-Temperature-and-Humidity-Sensor-p-5356.html) LoRaWAN CO₂/T/RH | Seeed Studio |
| Tank head-space CO₂ (0–10 000 ppm; often railed at 10 000) | [EM500-CO2](https://www.milesight.com/iot/product/lorawan-sensor/em500-co2) | Milesight |
| On-site rainfall — piezo (2024-07 →) | Ecowitt piezo rain gauge *(model to be confirmed)* | Ecowitt |
| On-site rainfall — tipping-bucket (2022–2024, faulty) | *make/model to be confirmed* | — |
| LoRaWAN gateway | *make/model to be confirmed* | — |
| In-tank cameras (leachate level) | *make/model to be confirmed* | — |

Leachate chemistry (TA, ions, pH, EC) is measured off-site by an accredited lab from the
pumped samples; the official weather reference is DWD station **03668 Nürnberg-Flughafen**.

## 2. Scope of this release (please read)

This release contains **only the "Fürth 2022" experiment** — the original soil and its
five treatments. In spring 2025, most of the pots were repurposed for a separate,
not-yet-published follow-on experiment; **that later work is not included here** and will
be released separately when it is written up.

**Continuing pots and the sensor time series.** After the 2025 changeover, only five pots
remain in the original Fürth-2022 soil: `000.A`, `100.A`, `200.A`, `400.A` and `400.E`.
The leachate/TA tables are cleanly separated by soil, so they contain Fürth-2022 rows
throughout. For the buried **soil-sensor** series we keep, after `2025-05-15`, **only
these five continuing pots** (readings from the repurposed pots are removed). Soil
temperature is reported at the site level and could not be attributed to individual pots,
so the temperature series **ends at** `2025-05-15`. The per-pot soil-CO₂ record
(`data/soil_co2_by_pot_daily.csv`, one sensor in each of the 20 pots) runs each sensor's
full life, with sensors failing progressively through 2023–2025. All other sensor products
(EC, pH, moisture) run to the end of 2025 for the continuing pots.

## 3. Repository layout

```
xxl-lysimeter-experiment-2022/
├── README.md                     ← this document
├── LICENSE                       ← CC-BY-4.0
├── CITATION.cff                  ← how to cite
├── CHANGELOG.md                  ← provenance & version history
├── data/                         ← the consumable tables (no code needed)
│   ├── xxl_lysimeter_TA_timeseries.csv   ★ MAIN FILE: TA + cumulative CO₂ export per pot
│   ├── xxl_lysimeter_data_wide.csv       full wide table (all leachate params, all volume variants)
│   ├── xxl_lysimeter_data_long.csv       tidy long format (one row per measurement)
│   ├── xxl_lysimeter_volumes.csv         per-sampling leachate volumes (3 estimates + source)
│   ├── xxl_lysimeter_metadata.json       units, molar masses, provenance, validation
│   ├── xxl_lysimeter_significance_vs_control.csv    per-window Welch/MWU test vs control
│   ├── xxl_lysimeter_mixedmodel_vs_control.csv      whole-period log-linear mixed-model effects
│   ├── xxl_lysimeter_volume_strategy_plausibility.csv  which A-pot volume model fits best
│   └── monitoring_*.csv                  leachate↔sensor pairing, correlations, survivorship
├── monitoring/                   ← buried-sensor inputs & weekly aggregates
│   ├── soil_{ec,ph,moisture}_{30,60}cm.xlsx, soil_temperature_30cm.xlsx, co2_concentrations.xlsx
│   ├── sensor_potlevel_weekly.csv, sensor_sitemean_weekly.csv
│   └── onsite_weather_extra.xlsx
├── weather/                      ← on-site vs official (DWD) rainfall & temperature
├── reference/                    ← feedstock characterization (XRD, XRF, grain size)
├── figures/                      ← analysis figures (branded PNGs)
└── code/                         ← scripts that turn the tables into the figures
```

## 4. Data dictionary (key files)

**`data/xxl_lysimeter_TA_timeseries.csv`** — the main file. One row per (pot, sampling
date).
- `variant` (e.g. `200.A`), `treatment` (`000/100/200/400/FINE`), `treatment_group_label`,
  `soil` (`FUERTH2022`), `date`, `days` (since 2022-05-15).
- `TA_umol_per_l` — measured leachate alkalinity as HCO₃⁻.
- `sampling_interval_days`, `rain_interval_mm`, `temp_mean_interval_C` — interval context
  (official DWD; `*_onsite_*` = on-site gauges).
- For each of the three volume models `{pumped, avgBD, dumpmodel}`:
  `TA_flux_mmol_per_m2_*` (per-interval export), `TA_cum_mmol_per_m2_*` (cumulative),
  `TA_CO2_t_per_ha_per_yr_*` (rate as CO₂), `TA_CO2cum_t_per_ha_*` (**cumulative CO₂
  export, the headline number**).

**`data/xxl_lysimeter_volumes.csv`** — leachate volume per sampling under three estimates:
`volume_pumped` (own pumped volume), `volume_avgBD` (A-pots estimated from parallel
B/C/D pots — the most plausible, see §6), `volume_dumpmodel` (pumped + logged overflow);
`volume_source` flags provenance.

**`data/xxl_lysimeter_data_wide.csv`** — 128 columns: every leachate parameter
(`*_umol_per_l`, `EC_*`, `pH_*`, ion sums), plus treatment/soil metadata and all volume/
flux variants. **`data/xxl_lysimeter_data_long.csv`** — the same in tidy long form
(`param`, `kind`, `unit`, `value_conc`, `below_lod`, `raw`, `source_file`).

**`data/xxl_lysimeter_significance_vs_control.csv`** — per-window difference of each
treatment vs control (`mean_treat`, `pct_vs_ctrl`, `p_welch`, `p_mwu`, Holm-corrected
`p_welch_holm`, `signif_holm`). **`..._mixedmodel_vs_control.csv`** — whole-period
log-linear mixed model (`effect_pct`, `ci_lo_pct`, `ci_hi_pct`, `p`) for concentration and
each volume model.

**`data/monitoring_leachate_sensor_paired.csv`** — each leachate sample paired with that
pot's nearest buried-sensor reading (leachate columns + `soil_ec_30/60cm`, `soil_ph_*`,
`soil_moisture_*`, `soil_co2_ppm`, …). **`..._correlation_potwise.csv`**,
**`..._correlation_ranked.csv`**, **`..._partialcorr_moisture_controlled.csv`**
(`r_raw` vs `r_partial_moisture`), **`..._sensor_survivorship.csv`** (active sensors per
month) are derived from it.

**`monitoring/sensor_{potlevel,sitemean}_weekly.csv`** — weekly buried-sensor values per
pot and as a site mean (`soil_moisture_*`, `soil_temp_30cm_C`, `soil_ec_*`, `soil_ph_*`,
`soil_co2_ppm`, `tank_air_co2_ppm`, `ambient_co2_ppm`).

**`data/soil_co2_by_pot_daily.csv`** — daily soil-CO₂ (ppm) for the buried ~20 cm sensor in
**each of the 20 pots** (`date`, `treatment`, `pot_id`, `sensor_serial`, `soil_co2_ppm`);
0, sub-400 (sub-atmospheric) and >40,000 ppm readings removed, control de-duplicated. Raw
per-pot exports in `monitoring/soil_co2_by_pot_raw/`. Rebuild figures with
`code/xxl_lysimeter_soil_co2.py`. The export labelled "MIXED" is a fourth FINE pot, included
here as `FINE200.MIXED`.

**`weather/weather_daily_combined.csv`** — daily `rain_onsite_mm` / `rain_official_mm`
(DWD 03668) and `temp_onsite_C` / `temp_official_C`.

Full units, molar masses and provenance are in **`data/xxl_lysimeter_metadata.json`**.

## 5. Methods, in brief

- **Surface area 0.406 m²/pot** (0.70 × 0.58 m); all area-normalised results use this.
- **CO₂ factor: 1 mol CO₂ per mol HCO₃⁻** — we report measured bicarbonate export as
  CO₂-equivalent (downstream/ocean losses excluded).
- **Gross export — not input-corrected.** Export = leachate concentration × drainage volume.
  It is *not* netted against the alkalinity carried in by the irrigation water. In the first
  summer (2022) each pot received ~111 L of hard municipal tap water (Infra Fürth, 16.7 °dGH,
  ≈ 5.1 mmol/L bicarbonate by ion balance) vs ~160 L rain. That input is of order **0.5 tCO₂e/ha**
  (up to ~0.6 as a strict mass-balance ceiling), roughly a **third** of the ~1.6 tCO₂e/ha
  gross cumulative — so the absolute CDR figures are an **upper bound** (irrigation-corrected
  ≈ 1.0–1.1 tCO₂e/ha, less again after downstream losses). This is common-mode across all pots, so it does **not** affect the
  treatment-vs-control comparison (irrigation-corrected treatment−control ≈ −0.06…+0.11).
- **Early phase (first ~90 days) is unrepresentative** — an initial flush (Birch effect:
  rewetting of the freshly built, disturbed soil after the first big drainage, Aug 2022), not
  weathering.
- **Below detection limit:** values reported as `<x` are set to 0 (flagged `below_lod` in
  the long table).
- **No dryness filter on EC.** The LSE01 reads EC and moisture from the same prongs and
  already temperature/conductivity-compensates its EC, so moisture is **not** an independent
  variable to gate or correct on — we use the raw buried EC. It would not matter anyway: the
  soil is wet whenever leachate is pumped (only 3 of 355 paired readings below 10 % VWC).
- **Validation:** this pipeline reproduces our original project notebook to a median
  relative error near zero (see `metadata.json`).

## 6. Volume models (why three)

The leachate volume for the A-Series pots that carries the alkalinity is only directly known for
some samplings (water had to be pumped out frequently to save the cameras in the tanks from
drowning). We provide three estimates; our analyses default to **`avgBD`** (A-pots
inferred from their parallel B/C/D siblings), which is the most plausible by an
out-of-sample check — see `data/xxl_lysimeter_volume_strategy_plausibility.csv` and
`figures/alt_FUERTH2022_volume_strategy_plausibility.png` (median |rel. dev| ≈ 6 % for
`avgBD` vs ≈ 42 % / 22 % for the alternatives).

## 7. Key findings (with figures)

- **Dose–response converges.** The early alkalinity peak is the Birch effect (rewetting
  flush of the freshly built soil, Aug 2022), not weathering; over the whole period no
  treatment differs significantly from control (per-window Welch, n = 4; whole-period mixed
  model). FINE trends highest (+6 % conc, +9 % export) but is not significant — and FINE is
  mineralogically a *different rock* (see §8).
  → `figures/TA_endpoint_by_treatment.png` (day-1,011 point plot with 95 % CI),
  `figures/slide1_TA_export_headline.png`, `alt_FUERTH2022_alkalinity_cumflux.png`,
  `alt_FUERTH2022_significance_vs_control.png`, `slide2_mixedmodel_forest.png`.
- **The irrigation-water blank.** In 2022 the pots were watered with ~111 L/pot of hard tap
  water (≈ 5.1 mmol/L HCO₃⁻) of order 0.5 tCO₂e/ha (up to ~0.6 ceiling), ~a third of gross — common to every
  pot, so it does not change the dose comparison but lowers the absolute CDR (see §5).
  → `figures/water_irrigation_share_2022.png`, `figures/TA_cumulative_gross_vs_net_tapwater.png`.
- **A buried EC sensor tracks leachate chemistry.** The 60 cm soil-EC probe correlates
  with leachate EC/Ca/Mg at **r ≈ 0.70** pooled (0.60–0.77 per treatment), and with
  leachate TA at r ≈ 0.45. **The 30 cm sensor barely works** (r ≈ 0.39). Soil-EC and soil
  moisture are read from the same LSE01 prongs, so moisture is not an independent confounder
  and we apply no dryness filter (only 3/355 paired points fall below 10 % VWC).
  → `figures/story_1_soilEC_predicts_leachateEC.png`,
  `monitoring_soilEC_vs_leachateEC_by_treatment_depth.png`.
- **The soil breathes.** Temperature → soil CO₂, soil CO₂ → leachate pH, soil CO₂ → leachate
  TA; a seasonal weathering engine, consistent across doses. Site-level chain (+0.58 / −0.74 /
  +0.58); with a sensor now in every pot, confirmed per-pot (+0.78 / −0.68 / +0.36).
  → `figures/story_2_weathering_mechanism_chain.png`, `story_3_seasonal_breathing.png`,
  `co2_1_seasonal_breathing_by_dose.png`.
- **Soil CO₂: what the living soil tells us — the weathering engine, not a carbon meter.**
  With a soil-CO₂ sensor in *every* pot (n = 4/dose): soil CO₂ runs 5–20× outdoor air and
  climbs with temperature, then **reverses above ~18 °C** as the soil dries (temperature ×
  moisture limit). Every dry→wet transition sets off a **repeated Birch effect** — a
  respiration burst (CO₂, only when warm) and a salt flush (EC, every time). CO₂ drives
  leachate acidity strongly (pH r = −0.68) but meters alkalinity only weakly (TA r = +0.36 vs
  EC ↔ TA +0.63) — the engine, not the meter. The basalt dose changes none of it (400 t/ha
  ~18 % low, n.s.).
  → `figures/co2_3_temp_moisture_engine.png`, `co2_5_birch_rewetting.png`,
  `co2_4_engine_not_meter.png`, `co2_2_dose_forest.png`, `co2_1_seasonal_breathing_by_dose.png`;
  data `data/soil_co2_by_pot_daily.csv`.
- **Confounders handled explicitly:** sensor age (survivorship falls from ~20 to a handful;
  time-detrended correlations survive). Dry-soil noise is a non-issue for the leachate
  comparison — the soil is always wet when leachate is pumped.
  → `figures/monitoring_sensor_survivorship.png`.

## 8. Feedstock characterization

The basalt is **"Eifelgold"** (Basalt-Union), a *basanite* — coarse batch (100/200/400
t/ha): median grain size ≈ 39 µm, BET 2.3 m²/g, max 478 kg CO₂/t. The **FINE** batch is
per XRD a *different rock* (44 % K-feldspar, 34 % natrolite, **5 % calcite**), so
"fine vs coarse" confounds grain size with mineralogy. Full XRD/XRF/grain-size tables and
sources: **`reference/feedstock_characterization.md`** (+ the two `.xlsx`).

## 9. Reproducing the figures

The `code/` scripts regenerate the sensor-derived tables and the series figures from the
data in this repository (they require `python3`, `pandas`, `numpy`, `matplotlib`,
`openpyxl`, `pillow`; `statsmodels`/`scipy` for the statistics). Figures are stamped with
our logo via `code/brand_standalone.py`. The raw-lab → leachate-table ingestion step lives
in our main experiment repository and is not needed to consume this dataset.

## 10. Further reading & references

Companion greenhouse work and background:

- Greenhouse EW series — *MRV Proxies for EW: a guided tour* (Part 1 of 9):
  https://www.carbon-drawdown.de/blog/2026-1-23-19-mrv-proxies-for-ew-a-guided-tour-through-our-data-from-our-two-year-greenhouse-experiment
- Report (PDF) — *Total Alkalinity and Electrical Conductivity as MRV Proxies for Enhanced
  Weathering:*
  https://www.carbon-drawdown.de/s/Total-Alkalinity-and-Electrical-Conductivity-as-MRV-Proxies-for-Enhanced-Weathering_-Insights-from-a-jtnx.pdf
- Greenhouse dataset: https://github.com/dirkpaessler/carbdown_greenhouse_2023_2024
  (Zenodo DOI 10.5281/zenodo.18360183)
- XXL Lysimeter project introduction (2022-02):
  https://www.carbon-drawdown.de/blog/2022-2-22-introducing-the-carbdown-xxl-lysimeter-project
- Photo logbook — building the XXL lysimeter (2022-06):
  https://www.carbon-drawdown.de/blog/2022-6-13-photo-logbook-building-the-xxl-lysimeter-weathering-experiment-part-1
- Biomass assessment of weathering in the XXL lysimeters (2022-10):
  https://www.carbon-drawdown.de/blog/2022-10-9-biomass-assessment-of-weathering-in-the-xxl-lysimeters
- Whitepaper — *What We Learned from the World's Largest Greenhouse Experiment* (Jan 2025),
  Tables 5–7 (feedstock characterization):
  https://www.carbon-drawdown.de/blog/2025-1-29-what-we-learned-from-the-worlds-largest-greenhouse-experiment

## 11. License & citation

Released under **CC-BY-4.0** (see `LICENSE`). Please cite as in `CITATION.cff`:

> Carbon Drawdown Initiative (2026). *XXL Lysimeter Experiment — Fürth 2022-2026 dataset.*
> Fürth, Germany. https://www.carbon-drawdown.de

---

*(c) 2022–2026 Carbon Drawdown Initiative — Carbdown GmbH · www.carbon-drawdown.de*
