# Changelog — XXL Lysimeter Experiment (Fürth 2022) dataset

Public releases of the Fürth-2022 dataset. Newest first.

---

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
  ≈ 5.1 mmol/L HCO₃⁻) ≈ 0.6 tCO₂e/ha ≈ 40 % of gross, so absolute CDR is an upper bound
  (irrigation-corrected ≈ 0.9–1.1 tCO₂e/ha). Common-mode across pots → treatment-vs-control
  comparisons unaffected. First ~90 days = initial flush / Birch effect. See README §5.
- Figures branded with the Carbon Drawdown Initiative logo.
- Released under **CC-BY-4.0**.

Supersedes the earlier *"XXL Lysimeter Experiment (started 2022) — Environmental data
2022–2024"* folder in `dirkpaessler/carbdown`.
