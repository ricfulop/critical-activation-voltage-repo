# Table II — Sub-Millisecond Binning Analysis

Supplemental Table II: Predictive onset verification via sub-millisecond voltage binning.

Raw 10 kHz voltage telemetry (from `../figure2/data/`) is averaged into time bins of width Δt (0.65–1.0 ms). Onset is defined as the first three consecutive bins where V ≥ Vc.

## Results

| Material | Vc (mV) | E_pred (V/m) | E_obs (V/m) | Error |
|----------|---------|-------------|-------------|-------|
| W | 89.1 | 1.04 | 1.12 ± 0.06 | < 8% |
| Pt | 49.3 | 0.71 | 0.79 ± 0.06 | 11% |

## Files

- `binning_table_supplemental.tex` — LaTeX source (REVTeX 4.2 format, `ruledtabular`)

## Rendering

```bash
cd table2
# The table is designed to be \input{} into the supplemental .tex file.
# To render standalone:
pdflatex -jobname=table2 "\documentclass[aps,prl,reprint]{revtex4-2}\usepackage{amsmath}\begin{document}\input{binning_table_supplemental.tex}\end{document}"
```

The binning analysis can also be reproduced from raw data:

```bash
cd ../figure2
python generate_figure2.py --onset
```
