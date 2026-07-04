# Changelog — XXL Lysimeter Experiment (Fürth 2022) dataset

Public releases of the Fürth-2022 dataset. Newest first.

---

## v1.0 — 2026-07-04 — First public release

- First open release of the **XXL Lysimeter Experiment**, soil **"Fürth 2022"**: leachate
  chemistry and cumulative bicarbonate export (local CDR), buried soil-sensor time series,
  on-site and official weather, and feedstock characterization. Companion to the two-year
  greenhouse dataset.
- **Scope: Fürth-2022 experiment only.** The 2025 "Griffelsberg" refill phase (new soil,
  new feedstocks) is intentionally excluded and will be released separately.
- **Sensor provenance after the 2025 refill:** only the five continuing Fürth-2022 pots
  (`000.A`, `100.A`, `200.A`, `400.A`, `400.E`) are retained in the soil-sensor products
  after `2025-05-15`; refilled-pot readings (now in Griffelsberg soil) are removed. Soil
  temperature is site-level and could not be pot-attributed, so it ends at the refill date;
  soil CO₂ (four continuing A-pots) and the other sensors (EC, pH, moisture, continuing
  pots) run to the end of 2025.
- Provenance: surface area **0.406 m²/pot**; CO₂ factor **1 mol CO₂ / mol HCO₃⁻**; leachate
  volume default model **`avgBD`** (best by out-of-sample plausibility check). Pipeline
  validated against the original project notebook (median relative error ≈ 0).
- Figures branded with the Carbon Drawdown Initiative logo.
- Released under **CC-BY-4.0**.

Supersedes the earlier *"XXL Lysimeter Experiment (started 2022) — Environmental data
2022–2024"* folder in `dirkpaessler/carbdown`.
