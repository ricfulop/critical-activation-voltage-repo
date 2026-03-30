# Figure 2 Reproducibility Package

Self-contained reproduction of **PRL Figure 2**: Resistivity anomaly onset predicted by the Critical Activation Voltage (Vc) from Voltivity theory, with gauge-length independence proof.

## Quick Start

```bash
pip install -r requirements.txt
python generate_figure2.py                # generates output/fig2_prl_v2.pdf
python generate_figure2.py --onset        # also prints fine-binning onset tables
```

## Contents

```
fig2-reproducibility-package/
├── README.md
├── requirements.txt
├── generate_figure2.py          # self-contained figure + onset extraction
├── analysis/
│   ├── __init__.py
│   └── iv_analysis.py           # IV analysis module (onset detection, thermal model)
├── data/                        # raw 10 kHz PicoScope IV recordings
│   ├── 2026-02-25 W 0.25mm 86mm run 1 - 4_32pm_combined.csv
│   ├── 2026-02-25 W 0.25mm 75mm run 2 - 4_44pm_combined.csv
│   ├── 2026-02-25 W 0.25mm 79mm run 3 - 4_50pm_combined.csv
│   ├── 2026-02-25 W 0.25mm 61mm run 4 - 4_54pm_combined.csv
│   ├── 2026-02-25 W 0.25mm 80mm run 5 - 4_59pm_combined.csv
│   └── 2026-02-25 Pt 0.127mm 69mm run 1 - 5_24pm_combined.csv
└── output/                      # generated figures appear here
```

## Data

All data was acquired on 2026-02-25 in Boulder, CO using a 16-bit PicoScope at 10 kHz sampling rate. Columns: `Time_ms`, `Voltage_V`, `Current_mV`, `Resistance_mOhm`. Current measured via a 100 A = 1 V shunt resistor.

| Wire | Material | Diameter (mm) | Gauge length (mm) | Atmosphere |
|------|----------|---------------|--------------------|------------|
| W run 1 | Tungsten | 0.25 | 86 | Air |
| W run 2 | Tungsten | 0.25 | 75 | Air |
| W run 3 | Tungsten | 0.25 | 79 | Air |
| W run 4 | Tungsten | 0.25 | 61 | Air |
| W run 5 | Tungsten | 0.25 | 80 | Air |
| Pt run 1 | Platinum | 0.127 (measured 0.131) | 69 | Air |

## Figure Description

**Panel (a):** Tungsten wire measured resistivity (solid orange) vs CRC Joule prediction from transient heat equation (dashed black). Green shading marks the anomaly region where measured ρ falls below the classical prediction. The vermillion star marks the predicted Vc = 89.1 mV (E = 1.04 V/m) onset.

**Panel (b):** Same for Platinum. Vc = 49.3 mV (E = 0.71 V/m).

**Panel (c):** Normalized resistivity ratio (ρ_eff / ρ_CRC) for five tungsten wires of different gauge lengths (61–86 mm), all collapsing together below the equilibrium line at 1.0. Demonstrates gauge-length independence of the anomaly.

## Thermal Model

The CRC Joule prediction uses a full transient heat equation:

    dT/dt = [J²ρ(T) − ε(T)σ(T⁴−T₀⁴)·4/d − κ(T)(T−T₀)·8/L²·f_diff] / (ρ_mass·Cp(T))

where f_diff = min(1, 2√(αt)/L) accounts for the finite thermal diffusion timescale (the wire center heats faster than a lumped model predicts in the first few seconds).

All material properties (ρ, Cp, κ, ε) are temperature-dependent, sourced from the CRC Handbook 97th edition, Desai et al., and Matula.

## Onset Extraction

The `--onset` flag performs a voltage-threshold analysis at sub-millisecond resolution:

1. Raw 10 kHz voltage data is averaged into time bins of width Δt
2. The first three consecutive bins where V ≥ Vc define the onset
3. E_onset = V_cross / L_gauge

This is repeated for Δt from 0.5 ms to 5 ms. The onset field E is stable across bin sizes, confirming the measurement is resolution-independent.

| Material | λ (V·µm) | Vc (mV) | Predicted E (V/m) | Measured E (V/m) |
|----------|----------|---------|--------------------|--------------------|
| W | 891 | 89.1 | 1.04 | 1.12 ± 0.06 |
| Pt | 493 | 49.3 | 0.71 | 0.79 ± 0.06 |

## License

Data and code provided for peer review and reproducibility. Please cite the associated publication.
