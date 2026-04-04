# Table I — Complete Dataset

Supplemental Table I: 73 field-activated experiments across 40 materials and 17 crystal families.

The dataset is stored in `../voltivity_dataset.csv`. The table in the Supplemental Material is generated directly from this CSV.

## Columns

| Column | Description | Units |
|--------|-------------|-------|
| `Material` | Material composition | — |
| `Family` | Crystal structure family | — |
| `E(V/cm)` | Applied electric field at onset | V/cm |
| `T_onset(K)` | Measured onset temperature | K |
| `r_fitted(um)` | Onset activation coherence length | μm |
| `Vc(V)` | Critical activation voltage (= E × r) | V |
| `k_soft` | Phonon softening factor | — |
| `DOI` | Source publication DOI | — |
| `Phenomenon` | `flash_sintering`, `electromigration`, `thin_film_switch`, or `macro_flash` | — |

## Key Statistics

- **40 materials**, 17 crystal structure families, 38 source publications
- **Vc range:** 0.005–2.7 V
- **Within-material CV:** < 1.9% mean (for materials with ≥ 2 measurements)
