# Universal Critical Activation Voltage for Phonon-Mediated Field-Driven Phenomena

[![DOI](https://zenodo.org/badge/DOI/PLACEHOLDER.svg)](https://doi.org/PLACEHOLDER)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Data, analysis code, and figures accompanying:

> **Fulop, R. & Gershenfeld, N.** "Universal Critical Activation Voltage for Phonon-Mediated Field-Driven Phenomena." *Submitted to Physical Review Letters* (2026).

## Overview

Field-driven phenomena — from flash sintering to electromigration — exhibit threshold fields spanning six orders of magnitude. We show that the product of the threshold electric field and the onset activation coherence length is a **universal critical activation voltage**:

```
Vc = E × r ≈ 0.1–2.7 V
```

Vc represents the threshold electrical work required to resonantly couple to the universal phonon damping peak at q\*/qD ≈ 0.73. This invariant unifies macroscopic thermal instabilities with the nanoscale Blech limit, establishing a universal phenomenological law for field–lattice coupling across 17 crystal families.

The invariant holds across **eight orders of magnitude in length scale**: from nanoscale thin-film switching (HfO₂ at 10⁻⁸ m) through microscale ceramic flash sintering to macroscopic metallic flash (W and Pt wires at 10⁻² m) — with zero free parameters.

## Dataset

`voltivity_dataset.csv` — 68 field-activated experiments compiled from 38 peer-reviewed publications.

| Column | Description | Units |
|--------|-------------|-------|
| `Material` | Material composition | — |
| `Family` | Crystal structure family | — |
| `E(V/cm)` | Applied electric field at onset | V/cm |
| `T_onset(K)` | Measured onset temperature | K |
| `r_fitted(um)` | Onset activation coherence length | μm |
| `lambda(V·um)` | Critical activation voltage: E × r | V·μm |
| `k_soft` | Phonon softening factor | — |
| `Ea(eV)` | Activation energy for conduction | eV |
| `sigma_0(S/m)` | Pre-exponential conductivity | S/m |
| `r_calc(um)` | Predicted coherence length | μm |
| `T_pred(K)` | Predicted onset temperature | K |
| `T_error%` | Prediction error | % |
| `DOI` | Source publication DOI | — |

To convert from the dataset units to Vc in Volts: **Vc (V) = λ (V·μm) × 10⁻⁴**.

### Key statistics

- **40 materials**, 17 crystal structure families, 38 source publications
- **Vc range:** 0.005–2.7 V (electromigration → covalent carbides)
- **Within-material CV:** < 1.9% mean (for materials with ≥2 measurements)
- **Prediction accuracy:** 2.6% mean |error| on onset temperature

### Vc hierarchy by bonding class

| Material class | Vc range | Physical origin |
|---|---|---|
| Electromigration (Cu, Al) | 5–14 mV | Grain-boundary diffusion, Z\* ≈ 5–10 |
| Elemental metals (Ni, W, Re) | 0.10–0.13 V | Low vacancy migration barrier |
| Perovskites | 0.23–0.30 V | Cooperative polaron cascades |
| Ionic oxides | 0.19–0.53 V | Intermediate defect barriers |
| Covalent carbides/nitrides | 0.32–2.7 V | Directional bonding, weak phonon coupling |

## Figures

### PRL Figure 1: Universal Unification

`figure_prl_unification.py` generates the two-panel PRL figure:

- **Panel (a):** Thermodynamic quantization — Vc distribution by material family
- **Panel (b):** Scale-invariant unification map — E vs r spanning 8 orders of magnitude

Additional data points beyond the CSV (plotted from literature):

| Phenomenon | Material | r (m) | E (V/m) | Vc (V) | Source |
|---|---|---|---|---|---|
| Thin-film switch | HfO₂ | 1×10⁻⁸ | 2×10⁸ | 2.0 | Lin et al., npj Quantum Mater. 9, 42 (2024) |
| Blech EM | Cu | 1×10⁻⁵ | 1400 | 0.014 | Lee et al., Appl. Phys. Lett. 79, 3236 (2001) |
| Blech EM | Al | 1×10⁻⁵ | 560 | 0.0056 | Blech, J. Appl. Phys. 47, 1203 (1976) |
| Macro flash | W | 8.6×10⁻² | 1.05 | 0.090 | This work |
| Macro flash | Pt | 6.9×10⁻² | 0.72 | 0.050 | This work |

```bash
# Generate PRL figure
pip install numpy pandas matplotlib
python figure_prl_unification.py
```

### Validation figures

`validate_lambda.py` reproduces the statistical analysis (parity plot, universal scaling collapse, λ hierarchy).

## Repository Structure

```
voltivity-repo/
├── voltivity_dataset.csv            # 68-point dataset
├── figure_prl_unification.py        # PRL Fig. 1 (unification figure)
├── figure_prl_unification.pdf       # Vector output
├── figure_prl_unification.png       # Raster output
├── validate_lambda.py               # Statistical analysis & validation figures
├── aps-prl-figures/
│   └── SKILL.md                     # APS/PRL figure design guidelines
├── README.md
└── LICENSE
```

## Citation

If you use this data or code, please cite:

```bibtex
@article{fulop2026vc,
  title   = {Universal Critical Activation Voltage for Phonon-Mediated
             Field-Driven Phenomena},
  author  = {Fulop, Ric and Gershenfeld, Neil},
  year    = {2026},
  note    = {Submitted to Physical Review Letters}
}
```

## Related Work

- **Universal phonon theory:** Ding, G. et al. "Unified theory of phonon in solids." *Nature Physics* **21**, 1911–1919 (2025). [doi:10.1038/s41567-025-03057-7](https://doi.org/10.1038/s41567-025-03057-7)
- **Boson peak universality:** Baggioli, M. & Zaccone, A. "Universal origin of boson peak vibrational anomalies." *Phys. Rev. Lett.* **122**, 145501 (2019).
- **Companion theory paper:** Fulop, R. et al. "Microscopic Origins of Voltivity: From Phonon Cascades to Anderson Localization." (In preparation, 2026).

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contact

Ric Fulop — ricfulop@mit.edu
Center for Bits and Atoms, Massachusetts Institute of Technology
ORCID: [0000-0002-9985-9151](https://orcid.org/0000-0002-9985-9151)
