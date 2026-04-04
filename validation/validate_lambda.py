#!/usr/bin/env python3
"""
Validation analysis for voltivity (λ) as a material constant.

Reproduces key statistical results from:
  Fulop, R. "Voltivity (λ): A New Fundamental Material Constant Governing
  Electric Field–Lattice Coupling in Crystalline Solids" (2026).

Usage:
    python scripts/validate_lambda.py

Requires: numpy, pandas, matplotlib
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    'text.usetex': False,
    'mathtext.fontset': 'stix',
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'STIX', 'DejaVu Serif'],
    'font.size': 10, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'legend.fontsize': 8, 'legend.title_fontsize': 8,
    'axes.linewidth': 0.5, 'axes.formatter.use_mathtext': True,
    'lines.linewidth': 0.8, 'lines.markersize': 4,
    'patch.linewidth': 0.5,
    'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.top': True, 'xtick.bottom': True,
    'ytick.left': True, 'ytick.right': True,
    'xtick.minor.visible': True, 'ytick.minor.visible': True,
    'xtick.major.size': 3.0, 'ytick.major.size': 3.0,
    'xtick.minor.size': 1.5, 'ytick.minor.size': 1.5,
    'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
    'xtick.minor.width': 0.5, 'ytick.minor.width': 0.5,
    'legend.frameon': True, 'legend.facecolor': 'white',
    'legend.edgecolor': 'white', 'legend.framealpha': 1,
    'axes.grid': False,
    'figure.dpi': 150, 'savefig.dpi': 600,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.05,
})

C_BLUE = '#0072B2'
C_ORANGE = '#E69F00'
C_GREEN = '#009E73'
C_VERMILLION = '#D55E00'
C_SKY = '#56B4E9'
C_PURPLE = '#CC79A7'
C_BLACK = '#000000'
C_GRAY = '#999999'

# ── Load data ────────────────────────────────────────────────────────────────

DATA_PATH = Path(__file__).parent.parent / "voltivity_dataset.csv"
FIGURES_PATH = Path(__file__).parent / "figures"
FIGURES_PATH.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} datapoints across {df['Material'].nunique()} materials "
      f"and {df['Family'].nunique()} crystal structure families.\n")

# ── 1. Within-material coefficient of variation ──────────────────────────────

print("=" * 70)
print("1. WITHIN-MATERIAL COEFFICIENT OF VARIATION (CV)")
print("=" * 70)

cv_results = []
for mat, grp in df.groupby("Material"):
    if len(grp) >= 2:
        lam_vals = grp["lambda(V·um)"].values
        cv = np.std(lam_vals, ddof=1) / np.mean(lam_vals) * 100
        cv_results.append({
            "Material": mat,
            "Family": grp["Family"].iloc[0],
            "n": len(grp),
            "lambda_mean": np.mean(lam_vals),
            "CV(%)": cv,
        })

cv_df = pd.DataFrame(cv_results).sort_values("CV(%)", ascending=False)

print(f"\nMaterials with n ≥ 2: {len(cv_df)}")
print(f"Materials with n ≥ 3: {len(cv_df[cv_df['n'] >= 3])}")
print(f"\nMean CV (n ≥ 2): {cv_df['CV(%)'].mean():.1f}%")
print(f"Mean CV (n ≥ 3): {cv_df[cv_df['n'] >= 3]['CV(%)'].mean():.1f}%")
print(f"Max CV:          {cv_df['CV(%)'].max():.1f}% ({cv_df.iloc[0]['Material']})")

print(f"\n{'Material':<30} {'Family':<15} {'n':>3} {'λ̄ (V·μm)':>12} {'CV (%)':>8}")
print("-" * 70)
for _, row in cv_df.iterrows():
    print(f"{row['Material']:<30} {row['Family']:<15} {row['n']:>3} "
          f"{row['lambda_mean']:>12,.0f} {row['CV(%)']:>8.1f}")

# ── 2. Prediction accuracy ──────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("2. PREDICTION ACCURACY (ONSET TEMPERATURE)")
print("=" * 70)

abs_err = df["T_error%"].abs()
print(f"\nMean |T_error|:   {abs_err.mean():.2f}%")
print(f"Median |T_error|: {abs_err.median():.2f}%")
print(f"95th percentile:  {abs_err.quantile(0.95):.1f}%")
print(f"Max |T_error|:    {abs_err.max():.1f}%")
print(f"Within ±5%:       {(abs_err <= 5).sum()}/{len(abs_err)} "
      f"({(abs_err <= 5).mean() * 100:.0f}%)")
print(f"Within ±10%:      {(abs_err <= 10).sum()}/{len(abs_err)} "
      f"({(abs_err <= 10).mean() * 100:.0f}%)")

# ── 3. Universal scaling collapse: log(r) vs log(E) ─────────────────────────

print(f"\n{'=' * 70}")
print("3. UNIVERSAL SCALING COLLAPSE")
print("=" * 70)

log_E = np.log10(df["E(V/cm)"].values)
log_r_norm = np.log10(df["r_fitted(um)"].values / df["lambda(V·um)"].values * df["E(V/cm)"].values)
log_r = np.log10(df["r_fitted(um)"].values)

# Regression: log(r) = slope * log(E) + intercept
from numpy.polynomial.polynomial import polyfit
coeffs = np.polyfit(log_E, log_r, 1)
slope, intercept = coeffs
r_squared = 1 - np.sum((log_r - (slope * log_E + intercept))**2) / \
                np.sum((log_r - np.mean(log_r))**2)

print(f"\nlog(r) vs log(E) regression:")
print(f"  Slope:     {slope:.2f} (expected: −1.00)")
print(f"  R²:        {r_squared:.2f}")

# ── 4. Lambda hierarchy by material family ───────────────────────────────────

print(f"\n{'=' * 70}")
print("4. λ HIERARCHY BY MATERIAL FAMILY")
print("=" * 70)

fam_stats = df.groupby("Family")["lambda(V·um)"].agg(["mean", "std", "count"])
fam_stats = fam_stats.sort_values("mean")

print(f"\n{'Family':<20} {'Mean λ':>10} {'Std':>8} {'n':>4}")
print("-" * 45)
for fam, row in fam_stats.iterrows():
    std_str = f"{row['std']:.0f}" if pd.notna(row["std"]) else "—"
    print(f"{fam:<20} {row['mean']:>10,.0f} {std_str:>8} {int(row['count']):>4}")

# ── 5. Generate figures ─────────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("5. GENERATING FIGURES")
print("=" * 70)

# Figure 1: Parity plot (T_onset predicted vs measured)
fig, ax = plt.subplots(figsize=(3.375, 3.375))
ax.scatter(df["T_onset(K)"], df["T_pred(K)"], c=C_BLUE, s=20, alpha=0.7,
           edgecolors="k", linewidths=0.3, zorder=3)
lims = [df["T_onset(K)"].min() - 50, df["T_onset(K)"].max() + 50]
ax.plot(lims, lims, "-", color=C_BLACK, linewidth=0.8, label="Perfect prediction")
ax.fill_between(lims, [l * 0.95 for l in lims], [l * 1.05 for l in lims],
                alpha=0.15, color=C_GREEN, label=r"$\pm$5% envelope")
ax.set_xlabel(r"Measured $T_\mathrm{onset}$ (K)")
ax.set_ylabel(r"Predicted $T_\mathrm{onset}$ (K)")
ax.legend(loc="upper left")
ax.set_xlim(lims)
ax.set_ylim(lims)
ax.set_aspect("equal")
fig.tight_layout()
fig.savefig(FIGURES_PATH / "parity_plot.png", dpi=300)
fig.savefig(FIGURES_PATH / "parity_plot.pdf")
print(f"  Saved figures/parity_plot.png")

# Figure 2: Universal scaling collapse
family_colors = {}
cmap = plt.cm.tab20
families = sorted(df["Family"].unique())
for i, fam in enumerate(families):
    family_colors[fam] = cmap(i / len(families))

fig, axes = plt.subplots(1, 2, figsize=(6.75, 3.0))

# Panel a: Raw r vs E
ax = axes[0]
for fam in families:
    mask = df["Family"] == fam
    ax.scatter(df.loc[mask, "E(V/cm)"], df.loc[mask, "r_fitted(um)"],
               c=[family_colors[fam]], s=15, alpha=0.8, label=fam,
               edgecolors="k", linewidths=0.2)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$E$ (V/cm)")
ax.set_ylabel(r"$r$ ($\mu$m)")
ax.set_title(r"$\mathbf{(a)}$ Raw data", fontsize=9, loc="left")
ax.legend(fontsize=4.5, ncol=2, loc="upper right",
          handlelength=0.8, labelspacing=0.2, borderpad=0.3)

# Panel b: r/λ vs E → collapse onto 1/E
ax = axes[1]
for fam in families:
    mask = df["Family"] == fam
    r_norm = df.loc[mask, "r_fitted(um)"] / df.loc[mask, "lambda(V·um)"]
    ax.scatter(df.loc[mask, "E(V/cm)"], r_norm,
               c=[family_colors[fam]], s=15, alpha=0.8, label=fam,
               edgecolors="k", linewidths=0.2)

E_line = np.logspace(np.log10(20), np.log10(2000), 100)
ax.plot(E_line, 1 / E_line, "-", color=C_BLACK, linewidth=1.0, label=r"$r/\lambda = 1/E$")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$E$ (V/cm)")
ax.set_ylabel(r"$r\,/\,\lambda$")
ax.set_title(r"$\mathbf{(b)}$ Universal collapse", fontsize=9, loc="left")
ax.legend(fontsize=4.5, ncol=2, loc="upper right",
          handlelength=0.8, labelspacing=0.2, borderpad=0.3)

fig.tight_layout()
fig.savefig(FIGURES_PATH / "universal_scaling_collapse.png", dpi=300)
fig.savefig(FIGURES_PATH / "universal_scaling_collapse.pdf")
print(f"  Saved figures/universal_scaling_collapse.png")

# Figure 3: Lambda by family (box plot)
df_plot = df.copy()
em_mask = df_plot["Phenomenon"] == "electromigration"
df_plot.loc[em_mask, "Family"] = "EM (" + df_plot.loc[em_mask, "Family"] + ")"

fam_stats_plot = df_plot.groupby("Family")["lambda(V·um)"].agg(["mean", "std", "count"])
fam_stats_plot = fam_stats_plot.sort_values("mean")
family_order_plot = fam_stats_plot.index.tolist()
data_by_fam = [df_plot[df_plot["Family"] == f]["lambda(V·um)"].values for f in family_order_plot]

fig, ax = plt.subplots(figsize=(6.75, 3.0))
bp = ax.boxplot(data_by_fam, labels=family_order_plot, patch_artist=True,
                medianprops=dict(color=C_VERMILLION, lw=0.8),
                whiskerprops=dict(lw=0.5), capprops=dict(lw=0.5),
                flierprops=dict(ms=3, markeredgewidth=0.3))
for i, patch in enumerate(bp["boxes"]):
    fam = family_order_plot[i]
    base_fam = fam.replace("EM (", "").replace(")", "") if fam.startswith("EM") else fam
    c = family_colors.get(base_fam, "0.7")
    patch.set_facecolor(c)
    patch.set_alpha(0.5 if fam.startswith("EM") else 0.7)
    patch.set_linewidth(0.5)
    if fam.startswith("EM"):
        patch.set_hatch("//")
ax.set_ylabel(r"$\lambda$ (V$\cdot\mu$m)")
ax.set_yscale("log")
plt.xticks(rotation=45, ha="right", fontsize=7)
fig.tight_layout()
fig.savefig(FIGURES_PATH / "lambda_hierarchy.png", dpi=300)
fig.savefig(FIGURES_PATH / "lambda_hierarchy.pdf")
print(f"  Saved figures/lambda_hierarchy.png")

print(f"\nDone. All figures saved to {FIGURES_PATH}/")
