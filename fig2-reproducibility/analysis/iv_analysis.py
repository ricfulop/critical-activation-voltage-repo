"""IV electrical analysis for flash onset detection.

Implements the Section 6.6 technique from the Voltivity paper (manuscript 21426):
1. Auto-detect voltage offset from low-current region
2. Bin V-I data at ΔJ intervals
3. Compute ρ(J) with Savitzky-Golay smoothing
4. Build thermal ρ_handbook(J) model via steady-state energy balance
5. Detect flash onset where measured ρ diverges from handbook prediction
6. Also compute d²ρ/dJ² for derivative-based onset confirmation
7. Bootstrap uncertainty estimation
8. Extract E_onset, J_onset, r_ed (electrodefect interaction length) from voltivity
"""

import numpy as np
import csv
from dataclasses import dataclass, field
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
from scipy.stats import linregress


@dataclass
class FlashOnsetResult:
    """Result of flash onset detection from IV data."""
    J_onset: float              # A/mm² at flash onset
    E_onset: float              # V/m at flash onset
    rho_onset: float            # µΩ·cm at onset
    T_onset_est_C: float        # Estimated temperature at onset
    V_onset: float              # Voltage at onset
    I_onset: float              # Current at onset
    t_onset_s: float            # Time at onset

    J_onset_err: float          # Bootstrap uncertainty
    E_onset_err: float

    r_um: float                 # Electrodefect interaction length (µm) = λ/E_onset
    lambda_Vum: float           # Voltivity used

    # LOC (loss of cohesion) if detected
    J_loc: float = np.nan
    E_loc: float = np.nan

    # Full traces for plotting
    J_binned: np.ndarray = None
    rho_binned: np.ndarray = None
    rho_smooth: np.ndarray = None
    drho_dJ: np.ndarray = None
    d2rho_dJ2: np.ndarray = None
    rho_handbook: np.ndarray = None      # thermal prediction ρ_thermal(J)
    T_handbook: np.ndarray = None        # T(J) from energy balance
    t_binned: np.ndarray = None          # binned time (s) corresponding to J_binned

    material: str = ""
    wire_diameter_mm: float = 0
    wire_length_mm: float = 0
    voltage_offset_mV: float = 0         # auto-detected offset
    onset_method: str = ""               # which method found onset
    dJ_dt: float = 0                     # ramp rate (A/mm²/s)


VOLTIVITY = {
    "W": 981,    # V·µm (BCC metal)
    "Pt": 1430,  # V·µm (FCC noble metal)
    "Ni": 1055,  # V·µm (FCC metal, estimated)
    "Ti": 1170,  # V·µm (measured in paper)
    "Cu": 480,   # V·µm
    "Ag": 620,   # V·µm
}

# ───────────────────────────────────────────────────────────────
# CRC Handbook resistivity data ρ(T) in µΩ·cm
# Sources: CRC 97th ed., Desai et al., White & Minges (W), Matula (Pt, Ni)
# Keys are temperature in Kelvin, values in µΩ·cm
# ───────────────────────────────────────────────────────────────
RHO_VS_T = {
    "W": {
        293: 5.39, 300: 5.49, 400: 7.83, 500: 10.3, 600: 13.0,
        700: 15.7, 800: 18.6, 900: 21.5, 1000: 24.5, 1100: 27.6,
        1200: 30.8, 1300: 34.1, 1400: 37.4, 1500: 40.8, 1600: 44.3,
        1700: 47.8, 1800: 51.4, 1900: 55.1, 2000: 58.8, 2200: 66.5,
        2400: 74.4, 2600: 82.6, 2800: 91.1, 3000: 99.8, 3200: 108.8,
        3400: 118.0, 3600: 127.5,
    },
    "Pt": {
        293: 10.6, 300: 10.8, 400: 14.6, 500: 18.4, 600: 22.2,
        700: 26.0, 800: 29.9, 900: 33.7, 1000: 37.6, 1100: 41.5,
        1200: 45.3, 1300: 49.2, 1400: 53.1, 1500: 57.0, 1600: 60.9,
        1700: 64.8, 1800: 68.7, 2000: 76.6,
    },
    "Ni": {
        293: 6.93, 300: 7.12, 400: 11.8, 500: 17.7, 600: 25.5,
        631: 69.0,   # Curie temperature anomaly
        700: 43.1, 800: 46.0, 900: 49.1, 1000: 52.3,
        1100: 55.6, 1200: 59.0, 1300: 62.5, 1400: 66.0, 1500: 69.6,
        1700: 77.0,
    },
}

# Thermal conductivity κ(T) in W/(m·K) for energy balance
KAPPA_VS_T = {
    "W": {300: 174, 500: 137, 700: 122, 1000: 107, 1500: 92, 2000: 82, 2500: 74, 3000: 68},
    "Pt": {300: 71.6, 500: 73.0, 700: 74.0, 1000: 76.0, 1500: 80.0, 2000: 84.0},
    "Ni": {300: 90.7, 500: 65.0, 600: 60.0, 631: 55.0, 700: 70.0, 1000: 68.0, 1500: 72.0},
}

# Total hemispherical emissivity ε(T)
EMISSIVITY_VS_T = {
    "W": {300: 0.03, 500: 0.04, 1000: 0.08, 1500: 0.13, 2000: 0.19, 2500: 0.25, 3000: 0.31},
    "Pt": {300: 0.04, 500: 0.06, 1000: 0.10, 1500: 0.15, 2000: 0.19},
    "Ni": {300: 0.05, 500: 0.07, 1000: 0.14, 1500: 0.19},
}

SIGMA_SB = 5.67e-8  # W/(m²·K⁴)


def _build_interpolator(data_dict, fill_value="extrapolate"):
    """Build scipy interpolator from {T_K: value} dict."""
    temps = np.array(sorted(data_dict.keys()), dtype=float)
    vals = np.array([data_dict[t] for t in temps], dtype=float)
    kind = "cubic" if len(temps) >= 4 else "linear"
    return interp1d(temps, vals, kind=kind, fill_value=fill_value,
                    bounds_error=False)


def _rho_interpolator(material):
    """Return ρ(T) interpolator in µΩ·cm for given material."""
    data = RHO_VS_T.get(material, RHO_VS_T["W"])
    return _build_interpolator(data)


def _T_from_rho(rho_uOhm_cm, material):
    """Invert ρ(T) → T(ρ) via the handbook curve."""
    data = RHO_VS_T.get(material, {})
    if not data:
        return np.nan
    temps = np.array(sorted(data.keys()), dtype=float)
    rhos = np.array([data[t] for t in temps], dtype=float)

    # For Ni, skip the Curie anomaly region for monotonic inversion
    if material == "Ni":
        mono = np.ones(len(rhos), dtype=bool)
        for i in range(1, len(rhos)):
            if rhos[i] <= rhos[i - 1]:
                mono[i] = False
        temps = temps[mono]
        rhos = rhos[mono]

    if rho_uOhm_cm <= rhos[0]:
        return float(temps[0])
    if rho_uOhm_cm >= rhos[-1]:
        return float(temps[-1])

    inv = interp1d(rhos, temps, kind="linear", bounds_error=False,
                   fill_value="extrapolate")
    return float(inv(rho_uOhm_cm))


def compute_thermal_rho_vs_J(J_array, material, wire_diameter_mm, wire_length_mm,
                              T_ambient=300.0):
    """Compute the expected purely-thermal ρ(J) via steady-state energy balance.

    At each J, solve for T such that Joule dissipation = radiation + conduction losses:
        J² · ρ(T) = ε(T)·σ·(T⁴ - T_amb⁴) · (P/A) + κ(T)·(T - T_amb)·(8/L²)

    where P/A = perimeter/cross-section = 4/d for a circular wire.

    Returns arrays of (rho_thermal, T_wire) for each J value.
    """
    rho_func = _build_interpolator(RHO_VS_T.get(material, RHO_VS_T["W"]))
    kappa_func = _build_interpolator(KAPPA_VS_T.get(material, KAPPA_VS_T["W"]))
    eps_func = _build_interpolator(EMISSIVITY_VS_T.get(material, EMISSIVITY_VS_T["W"]))

    d_m = wire_diameter_mm * 1e-3
    L_m = wire_length_mm * 1e-3
    perimeter_over_area = 4.0 / d_m  # m⁻¹

    # Max temperature in our handbook data
    T_max = max(RHO_VS_T.get(material, RHO_VS_T["W"]).keys())

    rho_thermal = np.full_like(J_array, np.nan)
    T_wire = np.full_like(J_array, np.nan)

    T_grid = np.linspace(T_ambient, T_max, 2000)
    rho_grid = rho_func(T_grid)

    for i, J_val in enumerate(J_array):
        if J_val <= 0:
            rho_thermal[i] = rho_func(T_ambient)
            T_wire[i] = T_ambient
            continue

        J_SI = J_val * 1e6  # A/mm² → A/m²
        # At each T, Joule = J² · ρ(T), losses = radiation + conduction
        rho_T = rho_func(T_grid) * 1e-8  # µΩ·cm → Ω·m
        joule = J_SI**2 * rho_T  # W/m³

        eps_T = eps_func(T_grid)
        kappa_T = kappa_func(T_grid)
        radiation = eps_T * SIGMA_SB * (T_grid**4 - T_ambient**4) * perimeter_over_area
        conduction = kappa_T * (T_grid - T_ambient) * 8.0 / L_m**2

        balance = joule - radiation - conduction

        # Find zero crossing (Joule = losses)
        sign_changes = np.where(np.diff(np.sign(balance)))[0]
        if len(sign_changes) > 0:
            idx = sign_changes[-1]  # highest T solution (stable)
            frac = balance[idx] / (balance[idx] - balance[idx + 1])
            T_eq = T_grid[idx] + frac * (T_grid[idx + 1] - T_grid[idx])
            rho_thermal[i] = float(rho_func(T_eq))
            T_wire[i] = float(T_eq)
        else:
            # No equilibrium → beyond thermal model (wire would melt/vaporize)
            rho_thermal[i] = np.nan
            T_wire[i] = np.nan

    return rho_thermal, T_wire


def load_iv_csv(filepath):
    """Load IV CSV file with columns Time_ms, Voltage_V, Current_mV, Resistance_mOhm."""
    t, V, I_mV = [], [], []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t_val = float(row["Time_ms"])
                v_val = float(row["Voltage_V"])
                i_val = float(row["Current_mV"])
            except (ValueError, TypeError):
                continue
            t.append(t_val)
            V.append(v_val)
            I_mV.append(i_val)

    return np.array(t) / 1000.0, np.array(V), np.array(I_mV)


def auto_fix_polarity(I_mV, V):
    """Detect and correct reversed leads. Returns (I_mV, V, flipped_I, flipped_V)."""
    flipped_I = False
    flipped_V = False

    # If the signal excursion is predominantly negative, flip it
    I_range = np.max(I_mV) - np.min(I_mV)
    if I_range > 1.0 and np.abs(np.min(I_mV)) > np.abs(np.max(I_mV)):
        I_mV = -I_mV
        flipped_I = True

    V_range = np.max(V) - np.min(V)
    if V_range > 0.01 and np.abs(np.min(V)) > np.abs(np.max(V)):
        V = -V
        flipped_V = True

    return I_mV, V, flipped_I, flipped_V


def auto_detect_offset(I_mV, V, threshold_mV=5.0):
    """Auto-detect current shunt offset from the lowest-current region.

    Uses the first N samples where |Current_mV| < threshold.
    Also estimates voltage offset from V at near-zero current.
    """
    mask = np.abs(I_mV) < threshold_mV
    if mask.sum() < 20:
        mask = np.argsort(np.abs(I_mV))[:100]

    I_offset = float(np.median(I_mV[mask]))
    V_offset = float(np.median(V[mask]))
    return I_offset, V_offset


ONSET_METHODS = ("bayesian_bic", "d2rho", "rls_slope")


def _detect_bayesian_bic(J, rho_smooth, search_start, delta_bic=6.0):
    """Bayesian BIC onset: find where quadratic model first beats linear.

    Scans forward from search_start. At each candidate breakpoint k,
    fits linear and quadratic models to data [0:k] and compares BIC.
    Onset = first k where ΔBIC > delta_bic with positive curvature.
    """
    n = len(J)
    for k in range(max(search_start, 5), n - 3):
        sl, il, _, _, _ = linregress(J[:k], rho_smooth[:k])
        resid_lin = rho_smooth[:k] - (il + sl * J[:k])
        ss_lin = np.sum(resid_lin**2)
        bic_lin = k * np.log(ss_lin / k + 1e-30) + 2 * np.log(k)

        coeffs = np.polyfit(J[:k], rho_smooth[:k], 2)
        resid_quad = rho_smooth[:k] - np.polyval(coeffs, J[:k])
        ss_quad = np.sum(resid_quad**2)
        bic_quad = k * np.log(ss_quad / k + 1e-30) + 3 * np.log(k)

        if coeffs[0] > 0 and bic_quad < bic_lin - delta_bic:
            return k, "bayesian_bic"

    return n - 1, "bayesian_bic_fallback"


def _detect_d2rho(J, rho_smooth, search_start):
    """d²ρ/dJ² zero-crossing onset detection."""
    drho = np.gradient(rho_smooth, J)
    d2rho = np.gradient(drho, J)
    for idx in range(search_start + 1, len(d2rho)):
        if d2rho[idx - 1] < 0 and d2rho[idx] >= 0:
            return idx, "d2rho_zero_crossing"
    # Fallback: dρ/dJ minimum
    search_region = drho[search_start:]
    return int(np.argmin(search_region)) + search_start, "drho_minimum"


def _detect_rls_slope(J, rho_smooth, search_start, forget=0.98, run_length=3):
    """Recursive least squares onset: detect when slope starts increasing."""
    n = len(J)
    theta = np.array([rho_smooth[0], 0.0])
    P = np.eye(2) * 100.0
    slopes = np.zeros(n)

    for i in range(n):
        x = np.array([1.0, J[i]])
        Px = P @ x
        denom = forget + x @ Px
        K = Px / denom
        e = rho_smooth[i] - x @ theta
        theta = theta + K * e
        P = (P - np.outer(K, Px)) / forget
        slopes[i] = theta[1]

    if n > 11:
        sw = min(11, n // 2 * 2 - 1)
        if sw % 2 == 0:
            sw += 1
        slopes_sm = savgol_filter(slopes, sw, 2)
    else:
        slopes_sm = slopes

    dslope = np.gradient(slopes_sm, J)
    run = 0
    for idx in range(search_start, len(dslope)):
        if dslope[idx] > 0:
            run += 1
            if run >= run_length:
                return idx - (run_length - 1), "rls_slope"
        else:
            run = 0

    return n - 1, "rls_slope_fallback"


def _find_onset(J, rho_smooth, search_start, detect_method="bayesian_bic"):
    """Dispatch to the selected onset detection method."""
    if detect_method == "bayesian_bic":
        return _detect_bayesian_bic(J, rho_smooth, search_start)
    elif detect_method == "d2rho":
        return _detect_d2rho(J, rho_smooth, search_start)
    elif detect_method == "rls_slope":
        return _detect_rls_slope(J, rho_smooth, search_start)
    else:
        raise ValueError(f"Unknown onset method: {detect_method}. "
                         f"Choose from {ONSET_METHODS}")


def analyze_flash_onset(filepath, material="W", wire_diameter_mm=0.25,
                         wire_length_mm=61.0, shunt_A_per_mV=0.1,
                         current_offset_mV=None, voltage_offset_V=None,
                         J_bin_width=0.5,
                         sg_window=21, sg_order=3,
                         n_bootstrap=500,
                         divergence_sigma=3.0,
                         detect_method="bayesian_bic"):
    """Full Section 6.6 analysis on an IV data file.

    Args:
        filepath: path to CSV with Time_ms, Voltage_V, Current_mV
        material: wire material (for voltivity lookup)
        wire_diameter_mm: wire diameter
        wire_length_mm: wire length (gauge length)
        shunt_A_per_mV: current calibration (100A=1V → 0.1 A/mV)
        current_offset_mV: shunt offset (None = auto-detect)
        voltage_offset_V: voltage probe offset (None = auto-detect)
        J_bin_width: current density bin width (A/mm²)
        sg_window: Savitzky-Golay window (bins)
        sg_order: Savitzky-Golay polynomial order
        n_bootstrap: number of bootstrap iterations
        divergence_sigma: σ threshold for handbook divergence onset
        detect_method: onset detection algorithm —
            'bayesian_bic' (default), 'd2rho', or 'rls_slope'

    Returns FlashOnsetResult.
    """
    t_s, V, I_mV = load_iv_csv(filepath)

    # Auto-correct reversed leads
    I_mV, V, flipped_I, flipped_V = auto_fix_polarity(I_mV, V)

    # Auto-detect offsets if not provided
    if current_offset_mV is None or voltage_offset_V is None:
        auto_I_off, auto_V_off = auto_detect_offset(I_mV, V)
        if current_offset_mV is None:
            current_offset_mV = auto_I_off
        if voltage_offset_V is None:
            voltage_offset_V = auto_V_off

    # Apply offsets
    I_A = (I_mV - current_offset_mV) * shunt_A_per_mV
    I_A = np.maximum(I_A, 0)
    V_corr = V - voltage_offset_V
    V_corr = np.maximum(V_corr, 0)

    # Wire geometry
    A_mm2 = np.pi * (wire_diameter_mm / 2) ** 2
    J = I_A / A_mm2  # A/mm²

    # Resistivity: ρ = R·A/L, R = V/I
    with np.errstate(divide="ignore", invalid="ignore"):
        R_ohm = np.where(I_A > 0.01, V_corr / I_A, np.nan)
    rho_uOhm_cm = R_ohm * (A_mm2 * 1e-6) / (wire_length_mm * 1e-3) * 1e8

    # Bin by current density
    J_max = np.nanmax(J)
    bins = np.arange(0, J_max + J_bin_width, J_bin_width)
    n_bins = len(bins) - 1

    J_binned = np.zeros(n_bins)
    rho_binned = np.zeros(n_bins)
    rho_std = np.zeros(n_bins)
    V_binned = np.zeros(n_bins)
    I_binned = np.zeros(n_bins)
    t_binned = np.zeros(n_bins)
    counts = np.zeros(n_bins, dtype=int)

    for i in range(n_bins):
        mask = (J >= bins[i]) & (J < bins[i + 1]) & np.isfinite(rho_uOhm_cm) & (I_A > 0.05)
        if mask.sum() > 0:
            J_binned[i] = np.mean(J[mask])
            rho_binned[i] = np.mean(rho_uOhm_cm[mask])
            rho_std[i] = np.std(rho_uOhm_cm[mask]) / np.sqrt(mask.sum())
            V_binned[i] = np.mean(V_corr[mask])
            I_binned[i] = np.mean(I_A[mask])
            t_binned[i] = np.mean(t_s[mask])
            counts[i] = mask.sum()

    # Filter to valid bins
    valid = counts > 10
    J_b = J_binned[valid]
    rho_b = rho_binned[valid]
    rho_s = rho_std[valid]
    V_b = V_binned[valid]
    I_b = I_binned[valid]
    t_b = t_binned[valid]

    lam = VOLTIVITY.get(material, 1000)

    if len(J_b) < 10:
        return FlashOnsetResult(
            J_onset=np.nan, E_onset=np.nan, rho_onset=np.nan,
            T_onset_est_C=np.nan, V_onset=np.nan, I_onset=np.nan,
            t_onset_s=np.nan, J_onset_err=np.nan, E_onset_err=np.nan,
            r_um=np.nan, lambda_Vum=lam, material=material,
        )

    # Savitzky-Golay smoothing
    win = min(sg_window, len(J_b) // 2 * 2 - 1)
    if win < 5:
        win = 5
    if win % 2 == 0:
        win += 1

    rho_smooth = savgol_filter(rho_b, win, min(sg_order, win - 1))

    # Compute dρ/dJ and d²ρ/dJ²
    drho_dJ = np.gradient(rho_smooth, J_b)
    d2rho_dJ2 = np.gradient(drho_dJ, J_b)

    # Build handbook thermal model ρ_thermal(J)
    rho_handbook, T_handbook = compute_thermal_rho_vs_J(
        J_b, material, wire_diameter_mm, wire_length_mm
    )

    # --- ONSET DETECTION ---
    search_start = len(J_b) // 5
    onset_idx, onset_method = _find_onset(J_b, rho_smooth, search_start, detect_method)

    J_onset = float(J_b[onset_idx])
    rho_onset = float(rho_smooth[onset_idx])
    V_onset = float(V_b[onset_idx])
    I_onset = float(I_b[onset_idx])
    t_onset = float(t_b[onset_idx])

    # E_onset = J · ρ in consistent units
    E_onset = J_onset * 1e6 * rho_onset * 1e-8  # V/m
    r_um = lam / E_onset if E_onset > 0 else np.nan

    # Temperature estimate from handbook
    T_est_K = _T_from_rho(rho_onset, material)
    T_est_C = T_est_K - 273.15

    # Bootstrap for uncertainty (reuses the same detection method)
    J_onsets_boot = []
    for _ in range(n_bootstrap):
        noise = np.random.normal(0, 1, len(rho_b)) * np.maximum(rho_s, 0.1)
        rho_boot = rho_b + noise
        rho_boot_smooth = savgol_filter(rho_boot, win, min(sg_order, win - 1))
        boot_idx, _ = _find_onset(J_b, rho_boot_smooth, search_start, detect_method)
        J_onsets_boot.append(J_b[min(boot_idx, len(J_b) - 1)])

    J_onset_err = float(np.std(J_onsets_boot))
    E_onset_err = J_onset_err * 1e6 * rho_onset * 1e-8

    # LOC detection (max resistivity point past onset)
    post_onset = rho_smooth[onset_idx:]
    if len(post_onset) > 1:
        loc_local = int(np.argmax(post_onset))
        loc_idx = loc_local + onset_idx
        J_loc = float(J_b[loc_idx]) if loc_idx > onset_idx else np.nan
        E_loc = J_loc * 1e6 * rho_smooth[loc_idx] * 1e-8 if not np.isnan(J_loc) else np.nan
    else:
        J_loc = np.nan
        E_loc = np.nan

    return FlashOnsetResult(
        J_onset=J_onset,
        E_onset=E_onset,
        rho_onset=rho_onset,
        T_onset_est_C=T_est_C,
        V_onset=V_onset,
        I_onset=I_onset,
        t_onset_s=t_onset,
        J_onset_err=J_onset_err,
        E_onset_err=E_onset_err,
        r_um=r_um,
        lambda_Vum=lam,
        J_loc=J_loc,
        E_loc=E_loc,
        J_binned=J_b,
        rho_binned=rho_b,
        rho_smooth=rho_smooth,
        drho_dJ=drho_dJ,
        d2rho_dJ2=d2rho_dJ2,
        rho_handbook=rho_handbook,
        T_handbook=T_handbook,
        t_binned=t_b,
        material=material,
        wire_diameter_mm=wire_diameter_mm,
        wire_length_mm=wire_length_mm,
        voltage_offset_mV=float(current_offset_mV),
        onset_method=onset_method,
        dJ_dt=_compute_ramp_rate(t_s, J),
    )


def _compute_ramp_rate(t_s, J):
    """Compute average ramp rate dJ/dt in A/mm²/s from raw time and J arrays."""
    duration = t_s[-1] - t_s[0]
    if duration <= 0:
        return 0.0
    J_max = np.nanmax(J)
    return float(J_max / duration)


@dataclass
class RampCorrectedResult:
    """Results of ramp-rate extrapolation to dJ/dt → 0."""
    material: str
    n_runs: int

    # Linear fit: J_onset = J0_true + alpha * dJ/dt
    J_onset_true: float        # intercept (A/mm²)
    J_onset_true_err: float    # std error on intercept
    alpha_s: float             # slope = kinetic delay (seconds)
    alpha_s_err: float
    r_squared: float
    p_value: float

    # Derived quantities at dJ/dt → 0
    E_onset_true: float        # V/m
    rho_at_onset: float        # µΩ·cm (mean across runs)
    r_true_um: float           # Electrodefect interaction length (µm) = λ / E_onset_true
    lambda_Vum: float

    # Per-run data for plotting
    dJ_dt_values: np.ndarray
    J_onset_values: np.ndarray
    J_onset_err_values: np.ndarray


def ramp_rate_correction(results, material=None):
    """Extrapolate J_onset to dJ/dt → 0 for a set of runs.

    Fits J_onset = J_onset_true + α · (dJ/dt) via OLS,
    then extrapolates to the quasi-static limit.

    Args:
        results: list of FlashOnsetResult
        material: filter to this material (None = use all)

    Returns RampCorrectedResult, or None if insufficient data.
    """
    filtered = [r for r in results
                if not np.isnan(r.J_onset) and r.dJ_dt > 0
                and (material is None or r.material == material)]

    if len(filtered) < 2:
        return None

    mat = filtered[0].material
    lam = filtered[0].lambda_Vum

    dj_dt = np.array([r.dJ_dt for r in filtered])
    j_on = np.array([r.J_onset for r in filtered])
    j_err = np.array([r.J_onset_err for r in filtered])
    rho_vals = np.array([r.rho_onset for r in filtered])

    if len(filtered) >= 3:
        slope, intercept, r_value, p_value, std_err = linregress(dj_dt, j_on)
        # Intercept uncertainty via bootstrap
        n_boot = 2000
        intercepts = []
        for _ in range(n_boot):
            idx = np.random.randint(0, len(dj_dt), size=len(dj_dt))
            if len(set(dj_dt[idx])) < 2:
                continue
            s, i, _, _, _ = linregress(dj_dt[idx], j_on[idx])
            intercepts.append(i)
        intercept_err = float(np.std(intercepts))
    else:
        # Only 2 points: simple line through both
        slope = (j_on[1] - j_on[0]) / (dj_dt[1] - dj_dt[0]) if dj_dt[1] != dj_dt[0] else 0
        intercept = j_on[0] - slope * dj_dt[0]
        r_value = 1.0
        p_value = 0.0
        intercept_err = float(np.mean(j_err))

    J_true = max(intercept, 0.1)  # physically must be positive
    rho_mean = float(np.mean(rho_vals))
    E_true = J_true * 1e6 * rho_mean * 1e-8
    r_true = lam / E_true if E_true > 0 else np.nan

    return RampCorrectedResult(
        material=mat,
        n_runs=len(filtered),
        J_onset_true=J_true,
        J_onset_true_err=intercept_err,
        alpha_s=slope,
        alpha_s_err=std_err if len(filtered) >= 3 else 0,
        r_squared=r_value**2,
        p_value=p_value,
        E_onset_true=E_true,
        rho_at_onset=rho_mean,
        r_true_um=r_true,
        lambda_Vum=lam,
        dJ_dt_values=dj_dt,
        J_onset_values=j_on,
        J_onset_err_values=j_err,
    )


def plot_ramp_correction(corrected_results, save_path=None):
    """Diagnostic figure: J_onset vs dJ/dt with linear extrapolation per material."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from config.figurestyle import apply_style, figsize_mm, C_BLUE, C_GREEN, C_ORANGE, DOUBLE_COL_MM
    apply_style()
    plt.rcParams.update({"lines.linewidth": 1.0})

    colors = {"W": C_BLUE, "Ni": C_GREEN, "Pt": C_ORANGE}
    markers = {"W": "o", "Ni": "s", "Pt": "D"}

    valid = [c for c in corrected_results if c is not None]
    if not valid:
        return None

    MM_TO_INCH = 1 / 25.4
    fig, (ax_j, ax_r) = plt.subplots(1, 2, figsize=(183 * MM_TO_INCH, 80 * MM_TO_INCH))

    for cr in valid:
        c = colors.get(cr.material, "#333333")
        m = markers.get(cr.material, "o")

        ax_j.errorbar(cr.dJ_dt_values, cr.J_onset_values,
                       yerr=cr.J_onset_err_values,
                       fmt=m, ms=4, color=c, capsize=2, lw=0.7,
                       label=cr.material, zorder=3)

        # Fit line extrapolated to 0
        x_fit = np.linspace(0, max(cr.dJ_dt_values) * 1.1, 100)
        y_fit = cr.J_onset_true + cr.alpha_s * x_fit
        ax_j.plot(x_fit, y_fit, "--", lw=0.7, color=c, alpha=0.6, zorder=2)

        # Mark the dJ/dt=0 intercept
        ax_j.plot(0, cr.J_onset_true, "*", ms=8, color=c, zorder=4,
                  markeredgecolor="black", markeredgewidth=0.3)

        # For panel b: compute r at each run and at the corrected value
        r_per_run = cr.lambda_Vum / (cr.J_onset_values * 1e6 * cr.rho_at_onset * 1e-8)
        ax_r.plot(cr.dJ_dt_values, r_per_run, m, ms=4, color=c, label=cr.material, zorder=3)
        ax_r.plot(0, cr.r_true_um, "*", ms=8, color=c, zorder=4,
                  markeredgecolor="black", markeredgewidth=0.3)

    ax_j.set_xlabel("Ramp rate, d$J$/d$t$ (A mm$^{-2}$ s$^{-1}$)")
    ax_j.set_ylabel("$J_{\\mathrm{onset}}$ (A mm$^{-2}$)")
    ax_j.set_xlim(left=-0.5)
    ax_j.legend(frameon=False)
    ax_j.spines["top"].set_visible(False)
    ax_j.spines["right"].set_visible(False)
    ax_j.text(-0.15, 1.05, "a", transform=ax_j.transAxes, fontsize=9,
              fontweight="bold", va="top")

    ax_r.set_xlabel("Ramp rate, d$J$/d$t$ (A mm$^{-2}$ s$^{-1}$)")
    ax_r.set_ylabel("Electrodefect interaction length, $r$ (µm)")
    ax_r.set_xlim(left=-0.5)
    ax_r.legend(frameon=False)
    ax_r.spines["top"].set_visible(False)
    ax_r.spines["right"].set_visible(False)
    ax_r.text(-0.15, 1.05, "b", transform=ax_r.transAxes, fontsize=9,
              fontweight="bold", va="top")

    # Add annotation table below
    fig.subplots_adjust(bottom=0.35)
    table_text = "Ramp-corrected (d$J$/d$t$ $\\rightarrow$ 0):\n"
    for cr in valid:
        flag = ""
        if cr.alpha_s < 0:
            flag = " [inverted: thermal regime dominates]"
        elif cr.n_runs < 3:
            flag = " [2 pts only]"
        table_text += (
            f"  {cr.material}: $J_{{\\mathrm{{onset}}}}^{{\\mathrm{{true}}}}$ = "
            f"{cr.J_onset_true:.1f} $\\pm$ {cr.J_onset_true_err:.1f} A mm$^{{-2}}$, "
            f"$r_{{\\mathrm{{ed}}}}$ = {cr.r_true_um:.0f} $\\mu$m, "
            f"$\\alpha$ = {cr.alpha_s:.2f} s "
            f"($R^2$ = {cr.r_squared:.2f}, $p$ = {cr.p_value:.3f}){flag}\n"
        )
    fig.text(0.05, -0.02, table_text, fontsize=5.5, va="top", fontfamily="sans-serif",
             linespacing=1.5)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        fig.savefig(save_path.replace(".png", ".pdf"), bbox_inches="tight")
    return fig


def plot_iv_analysis(result, save_path=None):
    """Generate publication-quality 5-panel figure (Nature/Science format).

    a) ρ(J) with handbook overlay
    b) dρ/dJ and d²ρ/dJ²
    c) V-I curve
    d) T(J) wire temperature
    e) Summary table
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from config.figurestyle import (
        apply_style, figsize_mm, panel_label as _panel_label, save_figure,
        C_BLUE, C_ORANGE, C_VERMILLION, C_GREEN, C_GRAY, C_PURPLE,
        DOUBLE_COL_MM,
    )
    apply_style()
    plt.rcParams.update({"lines.linewidth": 1.0, "legend.fontsize": 5.5})

    fig = plt.figure(figsize=figsize_mm(DOUBLE_COL_MM, 180))
    gs = fig.add_gridspec(3, 2, hspace=0.40, wspace=0.35)

    ax_rho = fig.add_subplot(gs[0, 0])
    ax_drho = fig.add_subplot(gs[0, 1])
    ax_vi = fig.add_subplot(gs[1, 0])
    ax_temp = fig.add_subplot(gs[1, 1])
    ax_summary = fig.add_subplot(gs[2, :])

    J = result.J_binned
    if J is None or len(J) == 0:
        return fig

    # ── Panel a: ρ(J) with handbook overlay ──
    ax_rho.plot(J, result.rho_binned, "o", ms=1.2, alpha=0.25, color=C_GRAY, zorder=1)
    ax_rho.plot(J, result.rho_smooth, "-", lw=1.0, color=C_BLUE, label="Measured", zorder=2)

    if result.rho_handbook is not None:
        hb_valid = np.isfinite(result.rho_handbook)
        ax_rho.plot(J[hb_valid], result.rho_handbook[hb_valid], "--", lw=1.0,
                    color=C_ORANGE, label="Handbook $\\rho(T)$", zorder=3)

    ax_rho.axvline(result.J_onset, color=C_VERMILLION, ls="--", lw=0.75,
                   label=f"Onset: {result.J_onset:.0f} A mm$^{{-2}}$")
    if not np.isnan(result.J_loc):
        ax_rho.axvline(result.J_loc, color=C_PURPLE, ls=":", lw=0.75,
                       label=f"LOC: {result.J_loc:.0f} A mm$^{{-2}}$")
    ax_rho.set_xlabel("Current density, $J$ (A mm$^{-2}$)")
    ax_rho.set_ylabel("Resistivity, $\\rho$ (µΩ cm)")
    ax_rho.legend(frameon=False, loc="upper left")
    ax_rho.text(-0.12, 1.05, "a", transform=ax_rho.transAxes, fontsize=9,
                fontweight="bold", va="top")
    ax_rho.spines["top"].set_visible(False)
    ax_rho.spines["right"].set_visible(False)

    # ── Panel b: dρ/dJ and d²ρ/dJ² ──
    ax_drho.plot(J, result.drho_dJ, "-", lw=0.75, color=C_GREEN, label="d$\\rho$/d$J$")
    ax_drho.axhline(0, color=C_GRAY, lw=0.3)
    ax_drho.axvline(result.J_onset, color=C_VERMILLION, ls="--", lw=0.75)
    ax_drho.set_xlabel("Current density, $J$ (A mm$^{-2}$)")
    ax_drho.set_ylabel("d$\\rho$/d$J$ (µΩ cm / A mm$^{-2}$)")
    ax_drho.spines["top"].set_visible(False)

    if result.d2rho_dJ2 is not None:
        ax2 = ax_drho.twinx()
        ax2.plot(J, result.d2rho_dJ2, "-", lw=0.6, color=C_PURPLE, alpha=0.7,
                 label="d²$\\rho$/d$J$²")
        ax2.axhline(0, color=C_PURPLE, lw=0.2, alpha=0.3)
        ax2.set_ylabel("d²$\\rho$/d$J$² (µΩ cm / (A mm$^{-2}$)²)", fontsize=5.5)
        ax2.tick_params(labelsize=5)
        ax2.spines["top"].set_visible(False)
        lines1, labels1 = ax_drho.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax_drho.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc="best",
                       fontsize=5)
    else:
        ax_drho.legend(frameon=False, loc="best")
        ax_drho.spines["right"].set_visible(False)

    ax_drho.text(-0.12, 1.05, "b", transform=ax_drho.transAxes, fontsize=9,
                 fontweight="bold", va="top")

    # ── Panel c: V-I curve ──
    I_trace = J * (result.wire_diameter_mm**2 * np.pi / 4)
    V_trace = result.rho_smooth * 1e-8 * J * 1e6 * result.wire_length_mm * 1e-3
    ax_vi.plot(I_trace, V_trace, "-", lw=0.75, color=C_ORANGE)
    ax_vi.axvline(result.I_onset, color=C_VERMILLION, ls="--", lw=0.75)
    ax_vi.set_xlabel("Current, $I$ (A)")
    ax_vi.set_ylabel("Voltage, $V$ (V)")
    ax_vi.text(-0.12, 1.05, "c", transform=ax_vi.transAxes, fontsize=9,
               fontweight="bold", va="top")
    ax_vi.spines["top"].set_visible(False)
    ax_vi.spines["right"].set_visible(False)

    # ── Panel d: Temperature ──
    from config.materials import MELTING_POINTS_K
    T_melt_K = MELTING_POINTS_K.get(result.material)
    T_melt_C = T_melt_K - 273.15 if T_melt_K else None

    if result.T_handbook is not None:
        T_valid = np.isfinite(result.T_handbook)
        T_C = result.T_handbook[T_valid] - 273.15
        J_hb = J[T_valid]
        if T_melt_C is not None:
            below_melt = T_C <= T_melt_C
            J_hb = J_hb[below_melt]
            T_C = T_C[below_melt]
        ax_temp.plot(J_hb, T_C, "-", lw=0.75, color=C_BLUE, label="Handbook $T(J)$")

        T_meas = np.array([_T_from_rho(r, result.material) - 273.15
                           for r in result.rho_smooth])
        T_meas_valid = np.isfinite(T_meas)
        if T_meas_valid.sum() > 0:
            ax_temp.plot(J[T_meas_valid], T_meas[T_meas_valid], "-", lw=0.75,
                        color=C_VERMILLION, alpha=0.7, label="From measured $\\rho$")

        ax_temp.axvline(result.J_onset, color=C_VERMILLION, ls="--", lw=0.75)
    else:
        ax_temp.text(0.5, 0.5, "No thermal model", ha="center", va="center",
                     transform=ax_temp.transAxes, color=C_GRAY)

    if T_melt_C is not None:
        ax_temp.axhline(T_melt_C, color="#D55E00", ls=":", lw=0.7, alpha=0.8)
        ax_temp.text(J[-1] * 0.98, T_melt_C, f" $T_{{\\mathrm{{melt}}}}$ = {T_melt_C:.0f} °C",
                     fontsize=5, color="#D55E00", ha="right", va="bottom")

    ax_temp.set_xlabel("Current density, $J$ (A mm$^{-2}$)")
    ax_temp.set_ylabel("Temperature (°C)")
    ax_temp.legend(frameon=False, loc="upper left", fontsize=5)
    ax_temp.text(-0.12, 1.05, "d", transform=ax_temp.transAxes, fontsize=9,
                 fontweight="bold", va="top")
    ax_temp.spines["top"].set_visible(False)
    ax_temp.spines["right"].set_visible(False)

    # ── Panel e: Summary table ──
    ax_summary.axis("off")
    ax_summary.text(-0.02, 1.05, "e", transform=ax_summary.transAxes, fontsize=9,
                    fontweight="bold", va="top")

    method_names = {
        "bayesian_bic": "Bayesian BIC",
        "bayesian_bic_fallback": "Bayesian BIC (fallback)",
        "d2rho_zero_crossing": "d²ρ/dJ² zero-crossing",
        "drho_minimum": "dρ/dJ minimum (fallback)",
        "rls_slope": "RLS slope",
        "rls_slope_fallback": "RLS slope (fallback)",
    }
    method_str = method_names.get(result.onset_method, result.onset_method)

    col1 = (
        f"{result.material}, Ø{result.wire_diameter_mm} mm × {result.wire_length_mm:.0f} mm\n\n"
        f"$J_{{\\mathrm{{onset}}}}$ = {result.J_onset:.1f} ± {result.J_onset_err:.1f} A mm$^{{-2}}$\n"
        f"$E_{{\\mathrm{{onset}}}}$ = {result.E_onset:.1f} ± {result.E_onset_err:.1f} V m$^{{-1}}$\n"
        f"$\\rho_{{\\mathrm{{onset}}}}$ = {result.rho_onset:.1f} µΩ cm"
    )
    col2 = (
        f"$T_{{\\mathrm{{onset}}}}$ ≈ {result.T_onset_est_C:.0f} °C\n"
        f"$\\lambda$({result.material}) = {result.lambda_Vum} V µm\n"
        f"$r_{{\\mathrm{{ed}}}}$ = {result.r_um:.1f} µm\n\n"
        f"Onset method: {method_str}\n"
        f"V offset: {result.voltage_offset_mV:.2f} mV"
    )
    ax_summary.text(0.02, 0.85, col1, transform=ax_summary.transAxes,
                    fontsize=6.5, va="top", linespacing=1.4)
    ax_summary.text(0.55, 0.85, col2, transform=ax_summary.transAxes,
                    fontsize=6.5, va="top", linespacing=1.4)

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        fig.savefig(save_path.replace(".png", ".pdf"), bbox_inches="tight")
    return fig
