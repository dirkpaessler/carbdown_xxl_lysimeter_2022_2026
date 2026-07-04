# Weather / environmental data — XXL Lysimeter (Fürth-Unterfarrnbach)

Site: ~49.49°N, 10.95°E (Fürth-Unterfarrnbach), Germany.

## ★ Combined table for downstream: `weather_daily_combined.csv`

One row per day (2022-01-01 …), **on-site vs. official** rainfall + temperature:
`date, rain_onsite_mm, rain_onsite_source, rain_official_mm, temp_onsite_C,
temp_official_C, rain_onsite_ecowitt_mm, rain_onsite_tipping_mm`.
- `rain_onsite_mm` = best on-site: **Ecowitt** where available (2024-07+), else the
  **tipping-bucket** gauge (2022-05 … 2024); `rain_onsite_source` says which.
- `rain_official_mm` / `temp_official_C` = **DWD 03668** (regional reference).

Cumulative on-site vs. official rainfall over the whole experiment:
`figures/weather_rainfall_onsite_vs_official.png`. On-site totals ~50–88 % of DWD.

## Files

- **`DWD_03668_Nuernberg_daily.csv`** — regional reference, **continuous since 2022**.
  Deutscher Wetterdienst station **03668 "Nürnberg (Flughafen)"**, ~10 km away. Daily
  `precip_mm` (RSK) and `temp_mean_C` (TMK). Public (DWD Climate Data Center).
  Annual rainfall: 2022 ≈ 533, 2023 ≈ 775, 2024 ≈ 691, 2025 ≈ 548 mm.
  Refresh: re-download `tageswerte_KL_03668_*_{hist,akt}.zip` from
  https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/

- **`onsite_ecowitt_daily.csv`** (+ `onsite_ecowitt_raw.xlsx`) — ★ **on-site station at
  the lysimeters** (Ecowitt Wittboy Pro HP2564, piezo rain gauge). Daily, **from
  2024-07-24**. Columns: `rain_daily_mm`, `temp_mean_C`, `temp_min_C`, `temp_max_C`,
  `humidity_pct`, `solar_wm2`. Validated vs DWD: daily correlation **0.70**, catches
  ~88 % of the DWD annual total (typical slight piezo under-catch; winter snow is
  under-caught more — e.g. Feb 2026 on-site 62 mm vs DWD 120 mm).

- **`onsite_tipping_2022.xlsx` / `_2023.xlsx` / `_2024.xlsx`** (+ parsed
  `onsite_tipping_daily.csv`) — on-site tipping-bucket gauge, daily. "Rain Total" is a
  daily-max counter; daily rainfall = its positive day-to-day change. Covers
  **2022-05-10 … 2025-01-01**, i.e. the pre-Ecowitt period. Under-catches (~48–63 % of
  DWD, daily corr 0.46) and had fault/stuck periods (e.g. a 19-day gap) — use with
  care; kept because it is the only on-site source before mid-2024.

## How it is used in the pipeline

Each sampling gets the rainfall & mean temperature over its sampling interval:
- `rain_interval_mm`, `temp_mean_interval_C` — from **DWD** (available for every
  sampling, whole experiment).
- `rain_interval_onsite_mm`, `temp_mean_interval_onsite_C` — from **on-site Ecowitt**
  (only intervals fully covered, i.e. 2024-07 onward → all Griffelsberg samplings).

**Recommendation:** for the 2025 Griffelsberg experiment prefer the on-site Ecowitt
rain (best spatial match); for the 2022–2025 Fürth experiment use DWD (on-site does
not reach back). Both are provided so the downstream can choose.

## Not usable / not fetched

- Earlier on-site tipping-bucket weekly export: "Rain Total" counter was non-monotonic
  and under-caught ~3× — discarded.
- Wunderground PWS **IFRTH236 "Farrnbachtal 2"** (~100 m): offline, history behind
  JavaScript, does not reach back to 2022 — not used.
