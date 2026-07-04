# XXL Lysimeter — Feedstock characterization

Sources: Carbon Drawdown Initiative whitepaper *"Learnings from running the world's
largest greenhouse EW experiment"* (Jan 2025), Tables 5–7; the XXL lysimeter setup
document (Table 1 + text, on Google Drive:
https://drive.google.com/file/d/1aBmdmXfDCmn-7_LnIozprQLFvE6kuPf3/view); and the
laser grain-size analysis `Eifelgold_coarse_laser_grain_size.xlsx` (Qmineral).

## Main basalt — "Eifelgold" (Basalt-Union / RPBL, Eifel, Germany)

Geologically a **basanite** (lower silica than a normal basalt; contains Si-poor
feldspathoids leucite ~13 % and nepheline ~9 %, rich in Na/K, dissolving at least as
fast as olivine ~11 %). This is why the basalt treatments show a strong early
weathering signal.

Two "Eifelgold" batches were used in the XXL lysimeters — but per the XRD
comparison (`Eifelgold_batches_XXL_GH_XRD.xlsx`, Schubert 2022 / FAU Erlangen vs
Qmineral) they are **mineralogically two different mafic volcanic rocks**, not just
two grinds of the same rock:

| Batch | Milled top size | Laser d10 / d50 / d90 | Used in |
|---|---|---|---|
| **Coarse** | < 1000–2000 µm | **3.9 / 38.5 / 447 µm** (94 % < 500 µm; ~37 % < 20 µm) | treatments 100/200/400 t/ha (`x00.A–D`); matches the greenhouse basanite |
| **Fine** | < 20 µm | — | treatment "fine-200" (`FINE`, the .E pots); 50/50 fine+coarse = "mixed-200" |

BET surface area (coarse, Table 5): **2.3 m²/g**. Max CDR potential: **478 kg CO₂/t**.
Curiously, a Hamburg surface-area measurement attributed a **bigger** surface area to
the coarse than to the fine batch (Schubert 2022) — consistent with the coarse
batch's large sub-20-µm fraction (~37 %).

**Mineralogy (XRD, wt%):**

| Mineral | XXL **coarse** (Schubert 2022) | XXL **fine** (Schubert 2022) | GH basanite (Qmineral) |
|---|---|---|---|
| Clinopyroxene/diopside | 40 | 13 | 49.4 |
| Plagioclase/anorthite | 16 | — | 7.7 |
| Leucite | 15 | — | 12.6 |
| Nepheline | 11 | — | 9.3 |
| Chlorite | 6 | — | — |
| Olivine/forsterite | 5 | 4 | 11.2 |
| Analcime | 4 | — | 1.3 |
| Natrolite (zeolite) | 3 | **34** | — |
| K-feldspar (microcline/sanidine) | — | **44** | — |
| **Calcite** | — | **5** | — |
| Sodalite / 2:1 silicates / apatite | — | — | 0.5 / 1.8 / 1.2 |

> ⚠️ **Interpretation caveat:** the FINE treatment is therefore **not** a clean
> grain-size comparison — the fine batch is a different rock dominated by K-feldspar
> (44 %) and the fast-weathering zeolite natrolite (34 %), and it contains **5 %
> calcite**, whose rapid dissolution alone can explain an early alkalinity surplus.
> Any "fine vs coarse" conclusions confound grain size with mineralogy.

**Chemistry (XRF, wt%):** SiO₂ 43.3 · Al₂O₃ 13.4 · Fe₂O₃ 11.0 · MgO 9.8 · CaO 12.7 ·
Na₂O 2.63 · K₂O 3.08 · TiO₂ 2.73 · P₂O₅ 0.55 · MnO 0.19 · LOI 0.6. Trace (ppm):
Ni 118, Cu 80, Co 51, V 286, Cr 205.

## Application rates (setup doc, Table 1; barrel 0.7 × 0.58 m = 0.406 m²)

| Treatment | t/ha | kg/m² | basalt per barrel |
|---|---|---|---|
| 100.A–D | 100 | 10 | 4.06 kg |
| 200.A–D | 200 | 20 | 8.12 kg |
| 400.A–D | 400 | 40 | 16.24 kg |

Applied 4–6 weeks after planting, mixed into the top 15 cm of soil.

> **Surface-area note:** the pipeline uses **0.406 m² per barrel** (0.7 × 0.58 m,
> `SURFACE_AREA_M2 = 0.406`), matching this setup document. The original project
> notebook used 0.48 m²; all area-normalised results (mmol/m², tCO₂/ha) are therefore
> ×0.48/0.406 = 1.182 higher than that earlier analysis. Concentrations, volumes and
> the mass-based validation are unaffected.

## Other feedstocks (Table 5)

- **Müllerkalk** (MKL, limestone): 85 % calcite / 14 % dolomite, 90 % < 365 µm,
  0.9 m²/g.
- **Glacial Rock Flour** (GRF, Greenland, Rock Flour Company): felsic glacial
  sediment, 90 % < 10 µm, mean 2.8 µm, 19.5 m²/g, 254 kg CO₂/t.
- Tichum Basalt (TIB) and Monticellite (MTC) from the 2025 Griffelsberg refill are
  not yet characterised in the Jan-2025 whitepaper.
