#!/usr/bin/env python3
"""Generate PRL Figure 2: Vc predictive onset + gauge-length independence.

Self-contained reproduction script. Requires only numpy, scipy, matplotlib.
All material data and styling are embedded — no external config imports.

Usage:
    python generate_figure2.py              # generates output/fig2_prl_v2.pdf
    python generate_figure2.py --onset      # also prints Vc onset extraction table

Three-panel figure:
  (a) W ρ_eff vs ρ_CRC with Vc onset marker
  (b) Pt ρ_eff vs ρ_CRC with Vc onset marker
  (c) Five W gauge lengths: ρ_eff/ρ_CRC ratio — gauge-length independence
"""

import os
import sys
import argparse
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d

# ════════════════════════════════════════════════════════════════
# MATERIAL DATA (CRC Handbook 97th ed., Desai, Matula)
# ════════════════════════════════════════════════════════════════

MELTING_POINTS_K = {"W": 3695, "Pt": 2041}

# ρ(T) in µΩ·cm
RHO_VS_T = {
    "W": {293: 5.39, 300: 5.49, 400: 7.83, 500: 10.3, 600: 13.0,
          700: 15.7, 800: 18.6, 900: 21.5, 1000: 24.5, 1100: 27.6,
          1200: 30.8, 1300: 34.1, 1400: 37.4, 1500: 40.8, 1600: 44.3,
          1800: 51.5, 2000: 59.0, 2200: 66.7, 2400: 74.4, 2600: 82.6,
          2800: 91.1, 3000: 99.8, 3200: 108.8, 3400: 118.0, 3600: 127.5},
    "Pt": {293: 10.6, 300: 10.8, 400: 14.6, 500: 18.4, 600: 22.2,
           700: 26.0, 800: 29.9, 900: 33.7, 1000: 37.6, 1100: 41.5,
           1200: 45.3, 1300: 49.2, 1400: 53.1, 1500: 57.0, 1600: 60.9,
           1700: 64.8, 1800: 68.7, 2000: 76.6},
}

# Cp(T) in J/(kg·K)
CP_VS_T = {
    "W": {293: 132, 400: 134, 600: 137, 800: 140, 1000: 143,
          1500: 152, 2000: 161, 2500: 170, 3000: 175, 3600: 182},
    "Pt": {293: 126, 400: 129, 600: 133, 800: 136, 1000: 140,
           1500: 148, 1800: 152, 2000: 155},
}

# κ(T) in W/(m·K)
KAPPA_VS_T = {
    "W": {300: 174, 500: 137, 700: 122, 1000: 107, 1500: 92,
          2000: 82, 2500: 74, 3000: 68},
    "Pt": {300: 71.6, 500: 73.0, 700: 74.0, 1000: 76.0,
           1500: 80.0, 2000: 84.0},
}

# ε(T) total hemispherical emissivity
EMISSIVITY_VS_T = {
    "W": {300: 0.03, 500: 0.04, 1000: 0.08, 1500: 0.13,
          2000: 0.19, 2500: 0.25, 3000: 0.31},
    "Pt": {300: 0.04, 500: 0.06, 1000: 0.10, 1500: 0.15, 2000: 0.19},
}

SIGMA_SB = 5.67e-8  # W/(m²·K⁴)
MASS_DENSITY = {"W": 19300, "Pt": 21450}  # kg/m³
RT_HANDBOOK = {"W": 5.39, "Pt": 10.60}    # µΩ·cm at 293 K

# Voltivity-predicted Critical Activation Voltages
VOLTIVITY_Vum = {"W": 891, "Pt": 493}     # V·µm
Vc = {m: v / 10000 for m, v in VOLTIVITY_Vum.items()}  # V

# ════════════════════════════════════════════════════════════════
# EXPERIMENTAL RUNS
# ════════════════════════════════════════════════════════════════

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

SHUNT = 0.1  # A/mV (100 A = 1 V shunt)

REPRESENTATIVE = [
    {"file": "2026-02-25 W 0.25mm 86mm run 1 - 4_32pm_combined.csv",
     "material": "W", "diameter": 0.25, "length": 86},
    {"file": "2026-02-25 Pt 0.127mm 69mm run 1 - 5_24pm_combined.csv",
     "material": "Pt", "diameter": 0.1311, "length": 69},
]

W_RUNS = [
    {"file": "2026-02-25 W 0.25mm 86mm run 1 - 4_32pm_combined.csv",
     "material": "W", "diameter": 0.25, "length": 86},
    {"file": "2026-02-25 W 0.25mm 75mm run 2 - 4_44pm_combined.csv",
     "material": "W", "diameter": 0.25, "length": 75},
    {"file": "2026-02-25 W 0.25mm 79mm run 3 - 4_50pm_combined.csv",
     "material": "W", "diameter": 0.25, "length": 79},
    {"file": "2026-02-25 W 0.25mm 61mm run 4 - 4_54pm_combined.csv",
     "material": "W", "diameter": 0.25, "length": 61},
    {"file": "2026-02-25 W 0.25mm 80mm run 5 - 4_59pm_combined.csv",
     "material": "W", "diameter": 0.25, "length": 80},
]

# ════════════════════════════════════════════════════════════════
# APS/PRL FIGURE STYLE
# ════════════════════════════════════════════════════════════════

C_ORANGE = '#E69F00'
C_SKY = '#56B4E9'
C_GREEN = '#009E73'
C_BLUE = '#0072B2'
C_VERMILLION = '#D55E00'
C_PURPLE = '#CC79A7'
C_BLACK = '#000000'
C_GRAY = '#999999'

plt.rcParams.update({
    'text.usetex': False,
    'mathtext.fontset': 'stix',
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'STIX', 'DejaVu Serif'],
    'font.size': 10, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'legend.fontsize': 8, 'legend.title_fontsize': 8,
    'axes.linewidth': 0.5, 'axes.formatter.use_mathtext': True,
    'lines.linewidth': 0.75, 'lines.markersize': 4,
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


def add_panel_label(ax, label, x=-0.15, y=1.08):
    ax.text(x, y, f'({label})', transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top', ha='left')


# ════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ════════════════════════════════════════════════════════════════

def _build_interpolator(data_dict):
    temps = np.array(sorted(data_dict.keys()), dtype=float)
    vals = np.array([data_dict[t] for t in temps], dtype=float)
    kind = "cubic" if len(temps) >= 4 else "linear"
    return interp1d(temps, vals, kind=kind, fill_value="extrapolate",
                    bounds_error=False)


def load_iv_csv(filepath):
    t, V, I_mV = [], [], []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t.append(float(row["Time_ms"]))
                V.append(float(row["Voltage_V"]))
                I_mV.append(float(row["Current_mV"]))
            except (ValueError, TypeError):
                continue
    return np.array(t) / 1000.0, np.array(V), np.array(I_mV)


def auto_fix_polarity(I_mV, V):
    if np.median(I_mV) < 0:
        I_mV = -I_mV
    if np.median(V) < 0:
        V = -V
    return I_mV, V


def auto_detect_offset(I_mV, V, threshold_mV=5.0):
    low = np.abs(I_mV) < threshold_mV
    if np.sum(low) > 100:
        return float(np.median(I_mV[low])), float(np.median(V[low]))
    return 0.0, 0.0


def load_and_process(run, bin_dt=0.1):
    """Load raw data, time-bin, compute transient CRC model."""
    mat = run["material"]
    filepath = os.path.join(DATA_DIR, run["file"])
    t_s, V_raw, I_mV = load_iv_csv(filepath)
    I_mV, V_raw = auto_fix_polarity(I_mV, V_raw)
    aI, aV = auto_detect_offset(I_mV, V_raw)
    I_A = np.maximum((I_mV - aI) * SHUNT, 0)
    V_c = np.maximum(V_raw - aV, 0)
    A = np.pi * (run["diameter"] / 2) ** 2
    L = run["length"] * 1e-3
    J_raw = I_A / A

    with np.errstate(divide="ignore", invalid="ignore"):
        R = np.where(I_A > 0.05, V_c / I_A, np.nan)
    rho_raw = R * (A * 1e-6) / L * 1e8

    early = (J_raw > 2) & np.isfinite(rho_raw)
    rho_rt = np.median(rho_raw[early][:1000]) if np.sum(early) > 100 else RT_HANDBOOK[mat]
    scale = rho_rt / RT_HANDBOOK[mat]

    # Vectorized time-binning
    edges = np.arange(t_s[0], t_s[-1] + bin_dt, bin_dt)
    idx = np.clip(np.digitize(t_s, edges) - 1, 0, len(edges) - 2)
    n = len(edges) - 1
    t_b = np.zeros(n); J_b = np.zeros(n); V_b = np.zeros(n)
    counts = np.zeros(n)
    np.add.at(t_b, idx, t_s)
    np.add.at(J_b, idx, J_raw)
    np.add.at(V_b, idx, V_c)
    np.add.at(counts, idx, 1)

    rho_b = np.full(n, np.nan)
    for k in range(n):
        if counts[k] == 0:
            continue
        m = idx == k
        fv = rho_raw[m]
        fv = fv[np.isfinite(fv)]
        if len(fv) > 0:
            rho_b[k] = np.median(fv)

    mask = (counts > 0) & np.isfinite(rho_b)
    t_b[mask] /= counts[mask]
    J_b[mask] /= counts[mask]
    V_b[mask] /= counts[mask]
    t_b, J_b, rho_b, V_b = t_b[mask], J_b[mask], rho_b[mask], V_b[mask]

    win = min(21, len(rho_b) // 2 * 2 - 1)
    rho_eff = savgol_filter(rho_b, win, 3) if win >= 5 else rho_b.copy()

    # Full transient thermal model
    rf = _build_interpolator(RHO_VS_T[mat])
    ef = _build_interpolator(EMISSIVITY_VS_T[mat])
    kf = _build_interpolator(KAPPA_VS_T[mat])
    cf = _build_interpolator(CP_VS_T[mat])
    d_m = run["diameter"] * 1e-3
    P_A = 4.0 / d_m
    rm = MASS_DENSITY[mat]
    Tm = MELTING_POINTS_K[mat]

    T_w = np.full(len(t_b), 300.0)
    for k in range(len(t_b) - 1):
        dt = t_b[k + 1] - t_b[k]
        if dt <= 0:
            T_w[k + 1] = T_w[k]; continue
        Tk = T_w[k]; J_SI = J_b[k] * 1e6
        rv = float(rf(Tk)) * 1e-8
        kap = float(kf(Tk)); cpT = float(cf(Tk)); eps = float(ef(Tk))
        joule = J_SI ** 2 * rv
        rad = eps * SIGMA_SB * (Tk ** 4 - 300 ** 4) * P_A
        t_el = max(t_b[k] - t_b[0], 0.01)
        alpha_T = kap / (rm * cpT)
        df = min(1.0, 2.0 * np.sqrt(alpha_T * t_el) / L)
        cond = kap * (Tk - 300) * 8.0 / L ** 2 * df
        dT_air = Tk - 300
        if dT_air > 0:
            Tf = (Tk + 300) / 2
            nu_air = 1.5e-5 * (Tf / 300) ** 1.7
            k_air = 0.026 * (Tf / 300) ** 0.8
            beta_air = 1.0 / Tf
            Ra = 9.81 * beta_air * dT_air * d_m ** 3 / nu_air ** 2 * 0.71
            cc_denom = (1 + (0.559 / 0.71) ** (9.0 / 16)) ** (8.0 / 27)
            Nu = (0.60 + 0.387 * Ra ** (1.0 / 6) / cc_denom) ** 2
            h_conv = Nu * k_air / d_m
            conv = h_conv * dT_air * P_A
        else:
            conv = 0.0
        T_w[k + 1] = max(300, min(Tk + (joule - rad - cond - conv) / (rm * cpT) * dt, Tm))

    rho_crc = np.array([float(rf(Ti)) for Ti in T_w]) * scale

    # Vc crossing time (0.8ms bins)
    dt_vc = 0.0008
    edges_vc = np.arange(t_s[0], t_s[-1] + dt_vc, dt_vc)
    idx_vc = np.clip(np.digitize(t_s, edges_vc) - 1, 0, len(edges_vc) - 2)
    n_vc = len(edges_vc) - 1
    V_vc = np.zeros(n_vc); t_vc = np.zeros(n_vc); c_vc = np.zeros(n_vc)
    np.add.at(V_vc, idx_vc, V_c)
    np.add.at(t_vc, idx_vc, t_s)
    np.add.at(c_vc, idx_vc, 1)
    valid_vc = c_vc > 0
    V_vc[valid_vc] /= c_vc[valid_vc]
    t_vc[valid_vc] /= c_vc[valid_vc]

    Vc_mat = Vc[mat]
    t_onset_vc = None
    v_v = V_vc[valid_vc]; t_v = t_vc[valid_vc]
    for i in range(len(v_v) - 2):
        if v_v[i] >= Vc_mat and v_v[i+1] >= Vc_mat and v_v[i+2] >= Vc_mat:
            t_onset_vc = t_v[i]; break

    return {
        "t": t_b, "J": J_b, "V": V_b,
        "rho_eff": rho_eff, "rho_crc": rho_crc, "T_wire": T_w,
        "scale": scale, "t_Vc": t_onset_vc, "L": L,
    }


# ════════════════════════════════════════════════════════════════
# Vc ONSET EXTRACTION (fine binning)
# ════════════════════════════════════════════════════════════════

def extract_onset_table(run, bin_sizes_ms=None):
    """Extract E_onset at each bin size via V >= Vc threshold."""
    if bin_sizes_ms is None:
        bin_sizes_ms = np.arange(0.5, 5.5, 0.05)
        bin_sizes_ms = np.round(bin_sizes_ms, 2)

    mat = run["material"]
    filepath = os.path.join(DATA_DIR, run["file"])
    t_s, V_raw, I_mV = load_iv_csv(filepath)
    I_mV, V_raw = auto_fix_polarity(I_mV, V_raw)
    aI, aV = auto_detect_offset(I_mV, V_raw)
    V_c = np.maximum(V_raw - aV, 0)
    L = run["length"] * 1e-3
    Vc_mat = Vc[mat]

    pre = t_s < (1.5 if mat == "W" else 0.5)
    sigma = np.std((V_raw - aV)[pre])

    results = []
    for dt_ms in bin_sizes_ms:
        dt = dt_ms / 1000
        n_per = max(1, round(dt * 10000))
        sigma_bin = sigma / np.sqrt(n_per)
        snr = Vc_mat / sigma_bin

        edges = np.arange(t_s[0], t_s[-1] + dt, dt)
        idx = np.clip(np.digitize(t_s, edges) - 1, 0, len(edges) - 2)
        n = len(edges) - 1
        V_b = np.zeros(n); t_b = np.zeros(n); c_b = np.zeros(n)
        np.add.at(V_b, idx, V_c)
        np.add.at(t_b, idx, t_s)
        np.add.at(c_b, idx, 1)
        ok = c_b > 0
        V_b[ok] /= c_b[ok]; t_b[ok] /= c_b[ok]
        V_v = V_b[ok]; t_v = t_b[ok]

        for i in range(len(V_v) - 2):
            if V_v[i] >= Vc_mat and V_v[i+1] >= Vc_mat and V_v[i+2] >= Vc_mat:
                results.append({
                    "dt_ms": dt_ms, "snr": snr, "n_per": n_per,
                    "t": t_v[i], "V_mV": V_v[i] * 1000,
                    "E": V_v[i] / L,
                })
                break

    return results, sigma


# ════════════════════════════════════════════════════════════════
# FIGURE GENERATION
# ════════════════════════════════════════════════════════════════

def generate_figure():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Loading and processing data...")

    rep_data = {}
    for run in REPRESENTATIVE:
        mat = run["material"]
        d = load_and_process(run)
        rep_data[mat] = d
        print(f"  {mat}: Vc crossing t={d['t_Vc']:.2f}s, E={Vc[mat]/d['L']:.2f} V/m")

    print("  Loading 5 W gauge lengths...")
    w_data = []
    for run in W_RUNS:
        w_data.append((run, load_and_process(run)))

    # Build figure
    fig = plt.figure(figsize=(6.75, 2.8))
    gs_outer = fig.add_gridspec(1, 2, wspace=0.30, width_ratios=[2.2, 1])
    gs_ab = gs_outer[0].subgridspec(1, 2, wspace=0.05)
    ax_w = fig.add_subplot(gs_ab[0, 0])
    ax_pt = fig.add_subplot(gs_ab[0, 1], sharey=ax_w)
    ax_ratio = fig.add_subplot(gs_outer[0, 1])

    # ── Panel (a): W ──
    d = rep_data["W"]
    ax_w.plot(d["t"], d["rho_eff"], "-", lw=0.9, color=C_ORANGE,
              label=r"Measured $\rho_\mathrm{eff}$")
    ax_w.plot(d["t"], d["rho_crc"], "--", lw=0.8, color=C_BLACK,
              label="CRC Joule prediction")
    both = np.isfinite(d["rho_eff"]) & np.isfinite(d["rho_crc"])
    anomaly = both & (d["rho_eff"] < d["rho_crc"])
    ax_w.fill_between(d["t"], d["rho_eff"], d["rho_crc"],
                      where=anomaly, alpha=0.25, color=C_GREEN,
                      label=r"$\rho_\mathrm{eff} < \rho_\mathrm{CRC}$")
    if d["t_Vc"] is not None:
        E_pred = Vc["W"] / d["L"]
        ax_w.axvline(d["t_Vc"], color=C_VERMILLION, ls="-", lw=1.0, zorder=5)
        ax_w.plot(d["t_Vc"], np.interp(d["t_Vc"], d["t"], d["rho_eff"]),
                  "*", ms=8, color=C_VERMILLION, zorder=6)
        ax_w.annotate(f'$V_c$ = {Vc["W"]*1000:.1f} mV\n$E$ = {E_pred:.2f} V/m',
                      xy=(d["t_Vc"], 90), fontsize=7, color=C_VERMILLION,
                      ha="left", va="center", xytext=(4, 0),
                      textcoords="offset points")
    ax_w.set_xlim(0, 45); ax_w.set_ylim(0, 100)
    ax_w.set_xlabel("Time (s)")
    ax_w.set_ylabel(r"Resistivity ($\mu\Omega\cdot$cm)")
    ax_w.set_title(r"$\mathbf{(a)}$ W, 0.25 mm, $L$ = 86 mm", fontsize=9, loc="left")

    # ── Panel (b): Pt ──
    d = rep_data["Pt"]
    ax_pt.plot(d["t"], d["rho_eff"], "-", lw=0.9, color=C_ORANGE,
               label=r"Measured $\rho_\mathrm{eff}$")
    ax_pt.plot(d["t"], d["rho_crc"], "--", lw=0.8, color=C_BLACK,
               label="CRC Joule prediction")
    both = np.isfinite(d["rho_eff"]) & np.isfinite(d["rho_crc"])
    anomaly = both & (d["rho_eff"] < d["rho_crc"])
    ax_pt.fill_between(d["t"], d["rho_eff"], d["rho_crc"],
                       where=anomaly, alpha=0.25, color=C_GREEN,
                       label=r"$\rho_\mathrm{eff} < \rho_\mathrm{CRC}$")
    if d["t_Vc"] is not None:
        E_pred = Vc["Pt"] / d["L"]
        ax_pt.axvline(d["t_Vc"], color=C_VERMILLION, ls="-", lw=1.0, zorder=5)
        ax_pt.plot(d["t_Vc"], np.interp(d["t_Vc"], d["t"], d["rho_eff"]),
                   "*", ms=8, color=C_VERMILLION, zorder=6)
        ax_pt.annotate(f'$V_c$ = {Vc["Pt"]*1000:.1f} mV\n$E$ = {E_pred:.2f} V/m',
                       xy=(d["t_Vc"], 90), fontsize=7, color=C_VERMILLION,
                       ha="left", va="center", xytext=(4, 0),
                       textcoords="offset points")
    ax_pt.set_xlim(0, 30); ax_pt.set_ylim(0, 100)
    ax_pt.set_xlabel("Time (s)")
    plt.setp(ax_pt.get_yticklabels(), visible=False)
    ax_pt.set_title(r"$\mathbf{(b)}$ Pt, 0.131 mm, $L$ = 69 mm", fontsize=9, loc="left")
    ax_pt.legend(fontsize=6, loc="lower right")

    # ── Panel (c): gauge-length independence ──
    ratio_colors = [C_BLUE, C_ORANGE, C_GREEN, C_VERMILLION, C_PURPLE]
    for i, (run, d) in enumerate(w_data):
        rho_eff = d["rho_eff"].copy()
        rho_crc = d["rho_crc"].copy()
        t = d["t"].copy()
        J = d["J"].copy()
        V = d["V"].copy()
        L = d["L"]

        both = np.isfinite(rho_eff) & np.isfinite(rho_crc) & (rho_crc > 0)
        ratio = np.full_like(rho_eff, np.nan)
        ratio[both] = rho_eff[both] / rho_crc[both]

        Vc_W = Vc["W"]
        vc_cross = np.where(V >= Vc_W)[0]
        t0 = t[vc_cross[0]] if len(vc_cross) > 0 else t[0]
        t_off = t - t0

        J_peak = np.max(J)
        stable = J >= 0.8 * J_peak
        last_stable = np.where(stable)[0][-1] if np.any(stable) else len(t) - 1
        start_idx = max(0, vc_cross[0] - 20) if len(vc_cross) > 0 else 0
        trim = slice(start_idx, last_stable + 1)
        t_off = t_off[trim]; ratio = ratio[trim]; both_trim = both[trim]

        if np.sum(np.isfinite(ratio)) > 11:
            finite = np.isfinite(ratio)
            win_r = min(7, np.sum(finite) // 2 * 2 - 1)
            if win_r >= 5:
                ratio[finite] = savgol_filter(ratio[finite], win_r, 2)

        J_max = float(np.max(d["J"]))
        duration = d["t"][-1] - d["t"][0]
        ramp = (J_max / duration * 60) if duration > 0 else 0
        lbl = f'{run["length"]}'
        valid = np.isfinite(ratio) & both_trim[:len(ratio)]
        ax_ratio.plot(t_off[valid], ratio[valid], "-", lw=0.7,
                      color=ratio_colors[i], label=lbl)

    ax_ratio.axhline(1.0, color=C_GRAY, ls=":", lw=0.5)
    ax_ratio.set_ylim(0.15, 1.10); ax_ratio.set_xlim(0, 42)
    xlim = ax_ratio.get_xlim()
    ax_ratio.fill_between([xlim[0], xlim[1]], 0, 1.0,
                          alpha=0.06, color=C_GREEN, zorder=0)
    ax_ratio.annotate(r"$\rho_\mathrm{eff} < \rho_\mathrm{CRC}$",
                      xy=(0.45, 0.35), xycoords="axes fraction", fontsize=7,
                      ha="center", color=C_GREEN, fontstyle="italic",
)
    ax_ratio.set_xlabel(r"Time from $V_c$ crossing (s)")
    ax_ratio.set_ylabel(r"$\rho_\mathrm{eff}\,/\,\rho_\mathrm{CRC}$")
    ax_ratio.legend(fontsize=5, loc="upper right", ncol=1,
                    title="$L$ (mm)",
                    title_fontsize=5, borderpad=0.3,
                    handlelength=1.0, labelspacing=0.2)
    ax_ratio.set_title(r"$\mathbf{(c)}$", fontsize=9, loc="left")

    out = os.path.join(OUTPUT_DIR, "fig2_prl_v2")
    fig.savefig(out + ".pdf", dpi=600, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(out + ".png", dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(f"\nFigure saved to:\n  {out}.pdf\n  {out}.png")


def run_onset_analysis():
    """Print fine-binning Vc onset extraction tables."""
    fine_bins = np.arange(0.65, 1.025, 0.05)
    coarse_bins = np.array([1, 2, 3, 4, 5])
    all_bins = np.unique(np.round(np.concatenate([fine_bins, coarse_bins]), 2))

    print("\n" + "=" * 70)
    print("Vc ONSET EXTRACTION — Fine Binning Analysis")
    print("=" * 70)

    for run in REPRESENTATIVE:
        mat = run["material"]
        L = run["length"] * 1e-3
        E_pred = Vc[mat] / L
        results, sigma = extract_onset_table(run, all_bins)

        print(f"\n{mat} (Vc = {Vc[mat]*1000:.1f} mV, L = {run['length']} mm, "
              f"σ_raw = {sigma*1000:.1f} mV)")
        print(f"  Predicted: E = Vc/L = {E_pred:.2f} V/m")
        print(f"\n  {'Bin(ms)':>8s} {'N/bin':>6s} {'σ_bin':>8s} {'SNR':>6s} "
              f"{'t(s)':>8s} {'V(mV)':>8s} {'E(V/m)':>8s}")
        print(f"  {'─'*8} {'─'*6} {'─'*8} {'─'*6} {'─'*8} {'─'*8} {'─'*8}")
        for r in results:
            print(f"  {r['dt_ms']:8.2f} {r['n_per']:6d} "
                  f"{sigma/np.sqrt(r['n_per'])*1000:8.2f} {r['snr']:6.1f} "
                  f"{r['t']:8.4f} {r['V_mV']:8.2f} {r['E']:8.2f}")

        E_vals = [r["E"] for r in results if r["snr"] >= 3.5]
        if E_vals:
            print(f"\n  Mean E (SNR≥3.5): {np.mean(E_vals):.2f} ± {np.std(E_vals):.2f} V/m"
                  f"  (predicted {E_pred:.2f})")


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PRL Figure 2 reproduction")
    parser.add_argument("--onset", action="store_true",
                        help="Run fine-binning Vc onset extraction")
    args = parser.parse_args()

    generate_figure()

    if args.onset:
        run_onset_analysis()
