# Critical Activation Voltage for Phonon-Mediated Field-Driven Phenomena

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Reproducibility package for:

> **Fulop, R. & Gershenfeld, N.** "Critical Activation Voltage for Phonon-Mediated Field-Driven Phenomena." *Submitted to Physical Review Letters* (2026).

## Quick Start

```bash
pip install -r requirements.txt

python figure1/generate_figure1.py          # PRL Figure 1
python figure2/generate_figure2.py          # PRL Figure 2
python figure2/generate_figure2.py --onset  # + onset extraction (Table II data)
python validation/validate_lambda.py        # Supplementary validation
```

## Repository Structure

```
voltivity-repo/
├── README.md
├── requirements.txt
├── voltivity_dataset.csv               # 73-experiment dataset (all phenomena)
│
├── figure1/                            # PRL Figure 1 — Universal Unification
│   ├── README.md
│   ├── generate_figure1.py
│   └── output/
│       ├── figure_prl_unification.pdf
│       └── figure_prl_unification.png
│
├── figure2/                            # PRL Figure 2 — Macroscopic Validation
│   ├── README.md
│   ├── generate_figure2.py
│   ├── requirements.txt
│   ├── analysis/
│   │   └── iv_analysis.py              # IV analysis module
│   ├── data/                           # Raw 10 kHz PicoScope recordings (6 runs)
│   └── output/
│       ├── fig2_prl_v2.pdf
│       └── fig2_prl_v2.png
│
├── table1/                             # Supplemental Table I — Complete Dataset
│   └── README.md                       # Column descriptions & key statistics
│
├── table2/                             # Supplemental Table II — Binning Analysis
│   ├── README.md
│   ├── binning_table_supplemental.tex  # LaTeX source (REVTeX ruledtabular)
│   └── output/
│
└── validation/                         # Supplementary Statistical Validation
    ├── README.md
    └── validate_lambda.py
```

## Dataset

`voltivity_dataset.csv` — 73 field-activated experiments compiled from 38 peer-reviewed publications, spanning flash sintering, electromigration, thin-film switching, and macroscopic metallic flash.

- **40 materials**, 17 crystal structure families
- **Vc range:** 0.005–2.7 V (electromigration → covalent carbides)
- **Within-material CV:** < 1.9% mean

| Material class | Vc range | Physical origin |
|---|---|---|
| Electromigration (Cu, Al) | 5–14 mV | Grain-boundary diffusion, Z\* ≈ 5–10 |
| Elemental metals (Ni, W, Re) | 0.10–0.13 V | Low vacancy migration barrier |
| Perovskites | 0.23–0.30 V | Cooperative polaron cascades |
| Ionic oxides | 0.19–0.53 V | Intermediate defect barriers |
| Covalent carbides/nitrides | 0.32–2.7 V | Directional bonding, weak phonon coupling |

## Figures and Tables

### Figure 1: Universal Unification

Two-panel figure showing (a) Vc distribution by bonding class and (b) E vs r scaling across eight orders of magnitude. Generated from `voltivity_dataset.csv`.

### Figure 2: Predictive Macroscopic Validation

Three-panel figure: (a) W and (b) Pt measured ρ_eff vs CRC thermal baseline, with anomaly onset at the predicted Vc; (c) gauge-length independence across five W wires.

| Material | Vc (mV) | Predicted E (V/m) | Measured E (V/m) |
|---|---|---|---|
| W | 89.1 | 1.04 | 1.12 ± 0.06 |
| Pt | 49.3 | 0.71 | 0.79 ± 0.06 |

### Table I: Complete Dataset

73-experiment tabulation (Supplemental Material). See `table1/README.md` for column descriptions.

### Table II: Sub-Millisecond Binning Analysis

Onset verification at 0.65–1.0 ms resolution, confirming the Vc prediction is resolution-independent. LaTeX source in `table2/`.

## Citation

```bibtex
@article{fulop2026vc,
  title   = {Critical Activation Voltage for Phonon-Mediated
             Field-Driven Phenomena},
  author  = {Fulop, Ric and Gershenfeld, Neil},
  year    = {2026},
  note    = {Submitted to Physical Review Letters}
}
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contact

Ric Fulop — ricfulop@mit.edu
Center for Bits and Atoms, Massachusetts Institute of Technology
[Google Scholar](https://scholar.google.com/citations?hl=en&user=N-PCwJ4AAAAJ&view_op=list_works&authuser=1)
