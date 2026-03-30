#!/usr/bin/env python3
"""
PRL Figure: Universal Voltage Hierarchy and Scale-Invariant Unification Map.

Panel (a): Vc distribution by material family (real data from voltivity_dataset.csv).
Panel (b): E vs r log-log map showing E × r = Vc = const (scale invariance).

Conversion: Vc (V) = λ (V·μm) × 1e-4   [since (V/cm)·(μm) = V × 1e-4]
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ── PRL figure style (APS/REVTeX-compatible) ─────────────────────────────────
USE_LATEX = True
try:
    plt.rcParams.update({'text.usetex': True})
    fig_test = plt.figure()
    fig_test.text(0.5, 0.5, r'$\alpha$')
    fig_test.savefig('/dev/null', format='png')
    plt.close(fig_test)
except Exception:
    USE_LATEX = False
    print("LaTeX not available — falling back to mathtext renderer.")

plt.rcParams.update({
    'text.usetex': USE_LATEX,
    'font.family': 'serif',
    'font.serif': ['cmr10', 'Computer Modern Roman', 'Times New Roman'],
    'mathtext.fontset': 'cm' if USE_LATEX else 'stix',
    'font.size': 10,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 7,
    'legend.title_fontsize': 8,
    'axes.linewidth': 0.5,
    'axes.formatter.use_mathtext': True,
    'lines.linewidth': 0.8,
    'patch.linewidth': 0.5,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'xtick.bottom': True,
    'ytick.left': True,
    'ytick.right': True,
    'xtick.minor.visible': True,
    'ytick.minor.visible': True,
    'xtick.major.size': 3.0,
    'ytick.major.size': 3.0,
    'xtick.minor.size': 1.5,
    'ytick.minor.size': 1.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.minor.width': 0.5,
    'ytick.minor.width': 0.5,
    'xtick.major.pad': 5.0,
    'ytick.major.pad': 5.0,
    'legend.frameon': True,
    'legend.facecolor': 'white',
    'legend.edgecolor': '0.85',
    'legend.framealpha': 1.0,
    'legend.handlelength': 1.2,
    'legend.labelspacing': 0.3,
    'axes.grid': False,
    'figure.dpi': 150,
    'savefig.dpi': 600,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

def bold(s):
    return rf'\textbf{{{s}}}' if USE_LATEX else s

def ital(s):
    return rf'\textit{{{s}}}' if USE_LATEX else s

# ── Okabe-Ito colorblind-safe palette ────────────────────────────────────────
C = {
    'blue':       '#0072B2',
    'orange':     '#E69F00',
    'green':      '#009E73',
    'purple':     '#CC79A7',
    'vermillion': '#D55E00',
    'sky':        '#56B4E9',
    'gray':       '#999999',
}

# ── Load and transform data ──────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / 'voltivity_dataset.csv'
df = pd.read_csv(DATA_PATH)

# SI units for plotting
df['r_m'] = df['r_fitted(um)'] * 1e-6         # μm → m
df['E_Vm'] = df['E(V/cm)'] * 100              # V/cm → V/m

# Broad material categories
CAT_MAP = {
    'FCC': 'Metals', 'BCC': 'Metals', 'HCP': 'Metals',
    'perovskite': 'Perovskites',
    'fluorite': 'Ionic Oxides', 'rutile': 'Ionic Oxides',
    'corundum': 'Ionic Oxides', 'spinel': 'Ionic Oxides',
    'ferrite': 'Ionic Oxides', 'garnet': 'Ionic Oxides',
    'pyrochlore': 'Ionic Oxides', 'wurtzite': 'Ionic Oxides',
    'oxide_composite': 'Ionic Oxides', 'composite': 'Ionic Oxides',
    'glass_ceramic': 'Ionic Oxides',
    'carbide': 'Covalent', 'nitride': 'Covalent',
}
df['Category'] = df['Family'].map(CAT_MAP)

# Split by phenomenon (all data now lives in the CSV)
df_flash    = df[df['Phenomenon'] == 'flash_sintering']
df_blech    = df[df['Phenomenon'] == 'electromigration']
df_macro    = df[df['Phenomenon'] == 'macro_flash']
df_thinfilm = df[df['Phenomenon'] == 'thin_film_switch']

CATS = ['Metals', 'Perovskites', 'Ionic Oxides', 'Covalent']
CAT_LABELS = ['Metals', 'Perovskites', 'Ionic\nOxides', 'Covalent']
CAT_COLORS = {
    'Metals':       C['blue'],
    'Perovskites':  C['purple'],
    'Ionic Oxides': C['orange'],
    'Covalent':     C['green'],
}
CAT_MARKERS = {
    'Metals':       'o',
    'Perovskites':  'd',
    'Ionic Oxides': 's',
    'Covalent':     '^',
}

# ── Create figure ─────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(6.75, 2.56),
    gridspec_kw={'width_ratios': [1, 1], 'wspace': 0.38},
)

# ═════════════════════════════════════════════════════════════════════════════
# Panel (a): Voltage Hierarchy — strip plot of Vc by material category
# ═════════════════════════════════════════════════════════════════════════════
np.random.seed(42)

# Flash sintering data (main dataset, circles by category)
for i, cat in enumerate(CATS):
    vc = df_flash.loc[df_flash['Category'] == cat, 'Vc(V)'].values
    if len(vc) == 0:
        continue
    jitter = np.random.uniform(-0.20, 0.20, len(vc))
    ax1.scatter(
        i + jitter, vc,
        c=CAT_COLORS[cat], s=25, alpha=0.75,
        edgecolors='k', linewidths=0.3, zorder=3,
    )
    med = np.median(vc)
    ax1.plot([i - 0.28, i + 0.28], [med, med],
             color=CAT_COLORS[cat], lw=1.2, zorder=2, solid_capstyle='round')

# Macroscopic metal flash (from CSV)
macro_jitter = np.random.uniform(-0.08, 0.08, len(df_macro))
ax1.scatter(
    0 + macro_jitter, df_macro['Vc(V)'].values,
    c=CAT_COLORS['Metals'], s=25, marker='*',
    edgecolors='k', linewidths=0.3, zorder=4,
    label='Macro Flash (W, Pt)',
)

# Blech electromigration (from CSV)
blech_jitter = np.random.uniform(-0.12, 0.12, len(df_blech))
ax1.scatter(
    0 + blech_jitter, df_blech['Vc(V)'].values,
    c=C['vermillion'], s=25, marker='p',
    edgecolors='k', linewidths=0.3, zorder=4,
    label='Blech EM (Cu, Al)',
)

# Thin-film switching (from CSV)
ax1.scatter(
    [2 + 0.15], df_thinfilm['Vc(V)'].values,
    c=C['sky'], s=25, marker='h',
    edgecolors='k', linewidths=0.3, zorder=4,
    label=r'Thin-Film Switch (HfO$_2$)',
)

ax1.set_yscale('log')
ax1.set_xticks(range(len(CATS)))
ax1.set_xticklabels(CAT_LABELS, fontsize=8)
ax1.set_ylabel(r'Critical Voltage, $V_c$ (V)')
ax1.set_ylim(0.003, 5)
ax1.set_xlim(-0.5, len(CATS) - 0.5)
ax1.legend(loc='upper left', fontsize=5.5, handletextpad=0.3, borderpad=0.4)
ax1.text(-0.22, 1.06, bold('(a)'), transform=ax1.transAxes,
         fontsize=10, va='top', ha='left')

# ═════════════════════════════════════════════════════════════════════════════
# Panel (b): Scale-invariant unification map E vs r (log-log)
# ═════════════════════════════════════════════════════════════════════════════
r_line = np.logspace(-9, 0.5, 300)

# Diagonal Vc = const reference lines
Vc_blech   = 0.014   # Electromigration (grain-boundary, Z*~10)
Vc_metals  = 0.10    # Bulk metals (Ni, W)
Vc_oxides  = np.median(df_flash.loc[df_flash['Category'] == 'Ionic Oxides', 'Vc(V)'])
Vc_carbide = 2.70    # Strongly covalent carbides (WC)

for vc_val, color, ls in [
    (Vc_blech,   C['vermillion'], (0, (3, 2))),
    (Vc_metals,  CAT_COLORS['Metals'],       '--'),
    (Vc_oxides,  CAT_COLORS['Ionic Oxides'], '-.'),
    (Vc_carbide, CAT_COLORS['Covalent'],     ':'),
]:
    ax2.plot(r_line, vc_val / r_line,
             ls=ls, color=color, lw=0.7, alpha=0.5)

# Direct labels on diagonal lines — compute correct rotation from axes geometry
def loglog_rotation(ax):
    """Compute display-space angle for slope -1 on a log-log plot."""
    xlim = np.log10(ax.get_xlim())
    ylim = np.log10(ax.get_ylim())
    bbox = ax.get_window_extent()
    data_aspect = (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    display_aspect = bbox.height / bbox.width
    return -np.degrees(np.arctan(display_aspect / data_aspect))

# Flash sintering data by category
for cat in CATS:
    mask = df_flash['Category'] == cat
    if mask.sum() == 0:
        continue
    ax2.scatter(
        df_flash.loc[mask, 'r_m'], df_flash.loc[mask, 'E_Vm'],
        c=CAT_COLORS[cat], marker=CAT_MARKERS[cat],
        s=25, alpha=0.8, edgecolors='k', linewidths=0.3, zorder=4,
        label=cat,
    )

# Blech electromigration (from CSV)
ax2.scatter(
    df_blech['r_m'], df_blech['E_Vm'],
    color=C['vermillion'], marker='p', s=25,
    edgecolors='k', linewidths=0.5, zorder=5,
    label='Blech EM',
)

# Macroscopic metal flash (from CSV)
ax2.scatter(
    df_macro['r_m'], df_macro['E_Vm'],
    color=CAT_COLORS['Metals'], marker='*', s=25,
    edgecolors='k', linewidths=0.5, zorder=5,
    label='Macro Flash',
)

# Thin-film switching (from CSV)
ax2.scatter(
    df_thinfilm['r_m'], df_thinfilm['E_Vm'],
    color=C['sky'], marker='h', s=25,
    edgecolors='k', linewidths=0.5, zorder=5,
    label=r'HfO$_2$ Switch',
)

ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlim(5e-9, 2e-1)
ax2.set_ylim(1e0, 5e8)
ax2.set_xlabel(r'Coherence Length, $r$ (m)')
ax2.set_ylabel(r'Electric Field, $E$ (V/m)')
ax2.legend(loc='lower left', fontsize=6, ncol=2,
           handlelength=1.0, columnspacing=0.8, borderpad=0.5,
           handletextpad=0.3)

# Force a draw so axes geometry is resolved before computing rotation
fig.canvas.draw()
rot = loglog_rotation(ax2)

# Place Vc labels directly on each diagonal line (staggered along r)
for vc_val, color, r_pos in [
    (Vc_blech,   C['vermillion'],            6e-7),
    (Vc_metals,  CAT_COLORS['Metals'],       3e-6),
    (Vc_oxides,  CAT_COLORS['Ionic Oxides'], 1e-5),
    (Vc_carbide, CAT_COLORS['Covalent'],     4e-5),
]:
    E_pos = vc_val / r_pos
    ax2.text(r_pos, E_pos * 1.5, rf'$V_c\!=\!{vc_val:.2f}$V',
             fontsize=5.5, color=color, ha='left', va='bottom',
             rotation=rot, rotation_mode='anchor')

# Scale-regime annotations (inside axes, away from edges)
for x, y, txt in [
    (8e-8, 1e8, 'Nanoscale'),
    (5e-4, 8e4, 'Microscale'),
    (2e-2, 8e0, 'Macroscale'),
]:
    ax2.text(x, y, ital(txt), fontsize=7, ha='center', color='0.45')

ax2.text(-0.14, 1.06, bold('(b)'), transform=ax2.transAxes,
         fontsize=10, va='top', ha='left')

# ── Save ──────────────────────────────────────────────────────────────────────
OUT = Path(__file__).parent
fig.savefig(OUT / 'figure_prl_unification.pdf')
fig.savefig(OUT / 'figure_prl_unification.png', dpi=300)
print(f"Saved: {OUT / 'figure_prl_unification.pdf'}")
print(f"Saved: {OUT / 'figure_prl_unification.png'}")
plt.show()
