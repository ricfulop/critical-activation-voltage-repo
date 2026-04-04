# Validation — Statistical Analysis

Supplementary statistical validation of the Vc invariant.

Reproduces:
- Within-material coefficient of variation (< 1.9%)
- Parity plot of predicted vs measured onset temperature
- Universal scaling collapse (λ hierarchy by crystal family)

## Usage

```bash
cd validation
python validate_lambda.py
```

Reads `../voltivity_dataset.csv`. Figures saved to `figures/`.
