---
name: aps-prl-figures
description: >-
  Create publication-quality scientific figures for APS journals (Physical Review Letters,
  Physical Review A–E, Reviews of Modern Physics) with proper serif typography, inward ticks,
  colorblind-safe palettes, and APS Style Guide compliance. Use when creating or advising on
  figures for APS journals, PRL plots, REVTeX manuscripts, matplotlib/pgfplots code for
  physics papers, or formatting figures for Physical Review submissions.
---

# SKILL: APS / Physical Review Letters Publication-Grade Figure Design

## Primary Goal

Create figures that are self-explanatory to physicists in adjacent subfields and reviewers at a glance.

**Core principle:** One figure = one clear physical result

-----

## Quick Reference Card

| Element | Specification |
|---|---|
| **Single-column width** | 8.5 cm (3.375 in) |
| **1.5-column width** | ~12.7 cm (5.0 in) |
| **Double-column width** | ~17.1 cm (6.75 in) |
| **PRFluids column** | 13.9 cm (5.5 in) — single-column journal |
| **Font family** | Computer Modern (LaTeX) or Times New Roman |
| **Alternative font** | Arial or Helvetica acceptable for labels |
| **Panel labels** | 8–10 pt, (a), (b), (c) with parentheses |
| **Axis labels** | 8–10 pt, units in parentheses |
| **Tick labels** | 8–9 pt |
| **Legend text** | 6–8 pt |
| **Minimum text height** | 2 mm at print size (~6 pt) |
| **Data point diameter** | ≥1 mm at print size |
| **Minimum line weight** | 0.18 mm (0.5 pt) |
| **Axis line weight** | 0.5 pt |
| **Data line weight** | 0.6–1.0 pt |
| **Resolution** | ≥600 dpi (vector preferred) |
| **Export format** | PDF or EPS (vector); TIFF or PNG (raster) |
| **Color online** | Free — no charge |
| **Color in print** | Charges apply — design for grayscale fallback |
| **Tick direction** | Inward, all four sides |
| **Minor ticks** | Visible |
| **Figure citation** | "Figure" at sentence start; "Fig." otherwise |

-----

## Typography Specifications

### Font Families

| Context | Font | Notes |
|---|---|---|
| **REVTeX/LaTeX manuscripts** | Computer Modern (cmr10) | Default; matches body text |
| **Alternative serif** | Times New Roman / STIX | Use `mathtext.fontset: stix` in matplotlib |
| **Sans-serif option** | Arial or Helvetica | Acceptable for figure labels only |
| **Mathematical variables** | Italic serif | Single-letter variables always italic |
| **Units** | Roman (upright) | Never italic: eV, cm, K, Hz |
| **Functions** | Roman (upright) | sin, cos, exp, ln, Re, Im, Tr, det |
| **Vectors** | Bold roman | **k**, **r**, **E** |
| **Chemical elements** | Roman (upright) | Fe, O, Si |
| **Greek as variables** | Italic | Default in LaTeX |

### Font Sizes (at final print size)

| Element | Size | Weight |
|---|---|---|
| Panel labels (a), (b), (c) | 8–10 pt | Bold or regular |
| Axis titles / labels | 8–10 pt | Regular |
| Tick labels | 8–9 pt | Regular |
| Legend text | 6–8 pt | Regular |
| Annotations / insets | 6–8 pt | Regular |
| Colorbar labels | 8–9 pt | Regular |

### Math Typography Rules (APS Style Guide §IV)

| Symbol type | Font style | Examples |
|---|---|---|
| Single-letter variables | *Italic* | *E*, *T*, *k*, *x* |
| Multi-letter functions | Roman | sin, cos, exp, ln, Tr, Re, Im |
| Units of measure | Roman | eV, cm, K, T, Hz, Ω |
| Multi-letter subscripts | Roman | E_lab, T_eff, k_max, V_bias |
| Single-letter sub/superscripts (abbreviations) | Italic (convention) | k_B, E_F, T_c |
| Vectors (3-vectors) | **Bold roman** | **k**, **r**, **B** |
| Chemical elements | Roman | Fe, Si, GaAs |
| Symmetry groups | Roman | SU(3), O(n) |
| Derivatives | Roman *d* or italic *d* | d*x*/d*t* (both conventions accepted) |

-----

## Axis & Label Conventions (APS Style Guide §S.3)

### Units

- Always enclose units in **parentheses** after the quantity name: `Energy (eV)`, `Temperature (K)`
- Use the form `R (10³ Ω)`, **not** `R × 10³ Ω`
- Thin space (half space) between compound unit parts: `mb/(MeV sr)`, **not** `mb/MeV/sr`
- Never use computer E-notation (e.g., `1E3`)

### Tick Values

- Prefer **integer tick values**: 0, 5, 10 — not 1.58, 3.16, 4.75
- Use **decimal points** (not commas): 0.2, not 0,2
- Always include digits on both sides of the decimal: `0.2`, **not** `.2`
- Consistent decimal places across all tick labels on the same axis
- Use **×10ⁿ** notation for axis multipliers, not E-notation

### Axis Style

- Tick marks point **inward** on all four sides of the plot
- Both **major and minor ticks** visible
- Unslashed zeros (standard, not crossed)
- Proper superscripts and subscripts in labels

-----

## Color System

### Qualitative/Categorical Data

Use the **Okabe-Ito colorblind-safe palette** (same recommendation as for any physics journal):

| Name | Hex | RGB | Typical use |
|---|---|---|---|
| Orange | #E69F00 | 230, 159, 0 | Primary accent |
| Sky Blue | #56B4E9 | 86, 180, 233 | Primary data |
| Bluish Green | #009E73 | 0, 158, 115 | Theory / model |
| Yellow | #F0E442 | 240, 228, 66 | Caution: low contrast |
| Blue | #0072B2 | 0, 114, 178 | Reference / threshold |
| Vermillion | #D55E00 | 213, 94, 0 | Important / alert |
| Reddish Purple | #CC79A7 | 204, 121, 167 | Tertiary |
| Black | #000000 | 0, 0, 0 | Baseline / text |
| Gray | #999999 | 153, 153, 153 | Secondary / background |

**Maximum categories:** 8 (beyond this, add shapes/patterns/line styles)

### Sequential/Continuous Data

| Colormap | Best for | Notes |
|---|---|---|
| **viridis** | General continuous | Default choice; perceptually uniform |
| **magma** | Intensity, temperature | Dark-to-bright |
| **plasma** | Magnitude, energy | Purple-to-yellow |
| **inferno** | Temperature | Black-to-yellow |
| **cividis** | Colorblind-critical | Blue-yellow only |

**Never use:** rainbow/jet — not perceptually uniform, fails in grayscale

### Diverging Data

| Colormap | Notes |
|---|---|
| **RdBu_r** | Classic; good for ± deviations |
| **coolwarm** | Muted; continuous diverging |
| **BrBG** | Colorblind-safe diverging |

Center color must represent zero/baseline. Symmetric scaling required.

### APS-Specific Color Rules

1. **Color online is free** — no charge for electronic publication
2. **Color in print costs** — design every figure to be **interpretable in grayscale**
3. **Pair color with line styles** — solid, dashed, dash-dot, dotted
4. **Pair color with marker shapes** — circles, squares, triangles, diamonds
5. **APS complies with WCAG** — use accessible color palettes
6. In captions, describe lines for both color and grayscale readers:
   - "Red solid line (theory)" and "blue dashed line (experiment)"
7. **Consistent semantic mapping** across all figures in a paper
8. Test with Coblis, Sim Daltonism, or `colorspacious` Python package

-----

## Design Principles

### 1. Self-Explanatory Figures

APS requires: *"Each figure must have a caption that makes the figure intelligible without reference to the text."*

- Figure + caption must stand alone
- Define all symbols in the caption or in a legend within the figure
- Every curve, marker, and shaded region must be identified

### 2. Data-Ink Ratio

Maximize the fraction of ink devoted to data:

- **Remove:** gridlines (unless essential), background shading, 3D effects, chart junk
- **Keep:** tick marks (inward, all sides), axis lines, data, direct labels
- **Prefer direct labels** over legends when space permits

### 3. Visual Hierarchy

| Principle | Application |
|---|---|
| **Data first** | Thickest lines / most saturated colors for primary data |
| **Theory second** | Thinner lines or different style for model curves |
| **Background last** | Gray, thin, or dashed for reference lines |
| **Error bands** | Semi-transparent fill (alpha 0.2–0.3) |

### 4. Subfigure Organization

- Label panels **(a)**, **(b)**, **(c)** — parentheses required by APS
- Place labels in **upper-left corner** of each panel
- Evenly space and align subpanels
- Share axes where data are directly comparable

-----

## File Formats & Naming

### Format Hierarchy

| Type | Preferred | Also accepted | Avoid |
|---|---|---|---|
| Plots / diagrams | **PDF** | EPS | Rasterized plots |
| Photographs / micrographs | **TIFF** (600 dpi) | PNG (600 dpi) | JPEG for line art |
| Mixed (plot + image) | **PDF** with embedded raster | EPS | Low-res composites |

### Naming Convention

`authorname_fig01.eps` or `authorname_fig01.pdf`

### Resolution Requirements

| Content | Minimum | Recommended |
|---|---|---|
| Line art / plots | 600 dpi | Vector (infinite) |
| Photographs | 300 dpi | 600 dpi |
| Mixed | 600 dpi | Vector + embedded raster |

-----

## Caption Conventions (APS Style Guide §S.2)

- Begins with **FIG.** followed by the arabic figure number and a period
- **Self-contained** — intelligible without the text
- Define all figure symbols, curves, and abbreviations
- Label subfigures (a), (b), etc., and describe each panel
- Specify units and what error bars represent
- Do **not** set footnotes to captions — incorporate the information directly
- Use "Figure" at the start of a sentence in the body text; "Fig." otherwise

-----

## Matplotlib Template for APS/PRL

```python
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# APS / PRL GLOBAL SETTINGS
# ============================================================
plt.rcParams.update({
    # Fonts — Computer Modern via LaTeX
    'text.usetex': True,
    'font.family': 'serif',
    'font.serif': ['cmr10'],        # Computer Modern Roman
    'mathtext.fontset': 'cm',

    # Font sizes (for 3.375 in wide figure)
    'font.size': 10,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 8,
    'legend.title_fontsize': 8,

    # Axes
    'axes.linewidth': 0.5,
    'axes.formatter.use_mathtext': True,

    # Line widths
    'lines.linewidth': 0.8,
    'lines.markersize': 4,
    'patch.linewidth': 0.5,

    # Ticks — INWARD on all four sides
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

    # Legend
    'legend.frameon': True,
    'legend.facecolor': 'white',
    'legend.edgecolor': 'white',
    'legend.framealpha': 1,
    'legend.handlelength': 1.375,
    'legend.labelspacing': 0.4,
    'legend.columnspacing': 1.0,

    # Grid (off by default — APS prefers clean)
    'axes.grid': False,

    # Saving
    'figure.dpi': 150,
    'savefig.dpi': 600,
    'savefig.format': 'pdf',
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'savefig.transparent': False,
    'path.simplify': True,
})

# ============================================================
# ALTERNATIVE: Times New Roman (no LaTeX required)
# ============================================================
# plt.rcParams.update({
#     'text.usetex': False,
#     'mathtext.fontset': 'stix',
#     'font.family': 'serif',
#     'font.serif': ['Times New Roman'],
# })

# ============================================================
# OKABE-ITO COLORBLIND-SAFE PALETTE
# ============================================================
COLORS = {
    'orange':     '#E69F00',
    'sky_blue':   '#56B4E9',
    'green':      '#009E73',
    'yellow':     '#F0E442',
    'blue':       '#0072B2',
    'vermillion': '#D55E00',
    'purple':     '#CC79A7',
    'black':      '#000000',
    'gray':       '#999999',
}

SEMANTIC = {
    'experiment':  '#0072B2',  # blue
    'theory':      '#D55E00',  # vermillion
    'simulation':  '#009E73',  # green
    'baseline':    '#4D4D4D',  # dark gray
    'error_fill':  '#CCCCCC',  # light gray
    'secondary':   '#56B4E9',  # sky blue
    'highlight':   '#E69F00',  # orange
}

# ============================================================
# FIGURE SIZE FUNCTIONS (APS specifications)
# ============================================================
def prl_single():
    """8.5 cm = 3.375 in (single column)"""
    return (3.375, 2.5)

def prl_single_square():
    """8.5 cm × 8.5 cm (single column, square)"""
    return (3.375, 3.375)

def prl_1p5():
    """~12.7 cm = 5.0 in (1.5 column)"""
    return (5.0, 3.5)

def prl_double():
    """~17.1 cm = 6.75 in (double column)"""
    return (6.75, 4.0)

# ============================================================
# PANEL LABELS — APS style with parentheses
# ============================================================
def add_panel_label(ax, label, x=-0.15, y=1.08):
    """Add APS-style panel label: (a), (b), etc."""
    ax.text(x, y, f'({label})', transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top', ha='left')

# ============================================================
# EXAMPLE USAGE
# ============================================================
if __name__ == '__main__':
    fig, axes = plt.subplots(1, 2, figsize=prl_double())

    for ax, label in zip(axes, ['a', 'b']):
        add_panel_label(ax, label)

    # Panel (a): line plot with error band
    ax = axes[0]
    x = np.linspace(0, 10, 100)
    y_exp = np.sin(x) + 0.1 * np.random.randn(100)
    y_thy = np.sin(x)
    ax.fill_between(x, y_thy - 0.15, y_thy + 0.15,
                     color=SEMANTIC['error_fill'], alpha=0.5)
    ax.plot(x, y_thy, '-', color=SEMANTIC['theory'], lw=1.0,
            label='Theory')
    ax.plot(x[::5], y_exp[::5], 'o', color=SEMANTIC['experiment'],
            ms=3, label='Experiment')
    ax.set_xlabel(r'Time (ns)')
    ax.set_ylabel(r'Signal (arb.\ units)')
    ax.legend()

    # Panel (b): scatter with colorbar
    ax = axes[1]
    xd = np.random.randn(80)
    yd = xd + 0.3 * np.random.randn(80)
    cd = np.sqrt(xd**2 + yd**2)
    sc = ax.scatter(xd, yd, c=cd, cmap='viridis', s=15, edgecolor='none')
    ax.plot([-3, 3], [-3, 3], '--', color=SEMANTIC['baseline'], lw=0.5)
    ax.set_xlabel(r'Predicted $E$ (eV)')
    ax.set_ylabel(r'Measured $E$ (eV)')
    plt.colorbar(sc, ax=ax, label=r'$|\mathbf{r}|$ (\AA)')

    plt.tight_layout()
    plt.savefig('example_prl_figure.pdf')
```

-----

## Pre-Submission Checklist

### Sizing & Format

- [ ] Figure planned for single-column width (8.5 cm) unless detail requires wider
- [ ] Vector format (PDF/EPS) for all plots and diagrams
- [ ] Raster images at ≥600 dpi
- [ ] File named `authorname_figNN.pdf`

### Typography

- [ ] Serif font (Computer Modern or Times) matching manuscript
- [ ] Variables italic, units roman, functions roman, vectors bold
- [ ] Axis labels: 8–10 pt at print size
- [ ] Tick labels: 8–9 pt at print size
- [ ] All text ≥2 mm height at print size (~6 pt minimum)
- [ ] Panel labels: (a), (b), (c) with parentheses

### Axes & Labels

- [ ] Units in parentheses: `Quantity (units)`
- [ ] Thin spaces in compound units: `mb/(MeV sr)`
- [ ] No computer E-notation
- [ ] Integer tick values where possible
- [ ] Consistent decimal places on each axis
- [ ] Proper ×10ⁿ notation for multipliers
- [ ] Decimal points (not commas); digits on both sides: `0.2`

### Ticks & Lines

- [ ] Ticks point **inward** on all four sides
- [ ] Minor ticks visible
- [ ] Major ticks: 3 pt; minor ticks: 1.5 pt
- [ ] Axis line width: 0.5 pt
- [ ] Data line width: ≥0.5 pt
- [ ] Data point diameter: ≥1 mm

### Color & Accessibility

- [ ] Interpretable in **grayscale** (for print)
- [ ] Line styles vary (solid, dashed, dash-dot, dotted)
- [ ] Marker shapes vary for different data series
- [ ] Colorblind-safe palette (Okabe-Ito or similar)
- [ ] No red-green only distinctions
- [ ] Consistent color → meaning mapping across paper
- [ ] Tested with colorblind simulator

### Captions

- [ ] Begins with "FIG. N."
- [ ] Self-contained (intelligible without main text)
- [ ] All symbols, curves, and abbreviations defined
- [ ] Each subfigure panel described
- [ ] Error bars / shaded regions explained
- [ ] Units specified where applicable

### Design

- [ ] Clear background, maximum contrast
- [ ] No chart junk (3D effects, shadows, gradients, unnecessary gridlines)
- [ ] Direct labels preferred over legends when space allows
- [ ] Error bands: semi-transparent fill
- [ ] Subfigures evenly spaced and aligned
- [ ] Figure placed near first text reference (not all at end)

-----

## Common Mistakes and Fixes

| Mistake | Fix |
|---|---|
| Sans-serif font in REVTeX paper | Use Computer Modern or Times |
| Ticks pointing outward | Set `xtick.direction: 'in'` and `ytick.direction: 'in'` |
| Ticks only on left/bottom | Enable ticks on all four sides |
| No minor ticks | Set `xtick.minor.visible: True` |
| Units without parentheses | Write `Energy (eV)`, not `Energy [eV]` or `Energy / eV` |
| Computer E-notation on axes | Use ×10ⁿ multiplier notation |
| Rainbow/jet colormap | Use viridis, magma, or cividis |
| Red-green distinction only | Use blue-orange + different line styles |
| Panel labels without parentheses | APS requires `(a)`, not just `a` |
| Rasterized plot at 72 dpi | Export as vector PDF; if raster, use ≥600 dpi |
| Comma decimal separator | Use decimal points: `0.2`, not `0,2` |
| `.2` without leading zero | Always write `0.2` |
| Ambiguous slash: `mb/MeV/sr` | Write `mb/(MeV sr)` |
| Legends obscuring data | Use direct labels or move legend outside |
| Inconsistent colors across figures | Define semantic mapping and reuse |
| Footnotes in figure captions | Incorporate info directly into caption text |
| Missing error bar definition | Always define in caption |
| Figure width too large for column | Plan for 8.5 cm (3.375 in) single column |

-----

## Physics-Specific Figure Types

### Common plot types in PRL and how to handle them:

| Figure type | Key consideration |
|---|---|
| Band structure / dispersion | High-symmetry points (Γ, K, M) as tick labels in roman; energy axis in eV |
| Phase diagram | Clear boundary lines; labeled phases; consistent color mapping |
| Parity plot (predicted vs. measured) | Diagonal reference line (dashed, gray); equal axis scales |
| Spectral data | Frequency/wavelength axis; intensity axis; peak labels |
| Time series / dynamics | Log scale when spanning decades; proper SI time units |
| Schematic / device diagram | Vector art; labeled components; consistent line weights |
| Density / contour plot | Colorbar with units; perceptually uniform colormap |
| Histograms | Proper bin widths; normalized if comparing; error bars if statistical |
| Error bar plots | Define ±1σ or 95% CI in caption; use caps sparingly |
| Insets | Same font sizes as main plot; clear axis labels; border if helpful |

-----

## References

1. **APS Journals Style Guide:** https://res.cloudinary.com/apsphysics/image/upload/v1715884920/aps-journals-style-guide_tnoyln.pdf
2. **APS Axis Labels and Scales:** https://journals.aps.org/authors/axis-labels-and-scales-on-graphs-h18
3. **APS Web Submission Guidelines:** https://journals.aps.org/authors/web-submission-guidelines-physical-review
4. **PRL Information for Contributors:** https://journals.aps.org/prl/info/infoL.html
5. **PRL Tips for Authors:** https://journals.aps.org/prl/authors/tips-authors-physical-review-physical-review-letters
6. **REVTeX 4.2 Author Guide:** https://cdn.journals.aps.org/files/revtex/apsguide4-1.pdf
7. **physrev_mplstyle (matplotlib):** https://github.com/hosilva/physrev_mplstyle
8. **Wong, B.** "Color blindness." *Nature Methods* 8, 441 (2011)
9. **Okabe, M. & Ito, K.** "Color Universal Design." University of Tokyo (2002)
10. **Tufte, E.R.** *The Visual Display of Quantitative Information* (Graphics Press, 2001)

-----

## Version History

- **v1.0** (2026-03): Initial version based on APS Journals Style Guide, PRL contributor guidelines, and community best practices
