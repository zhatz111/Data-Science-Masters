"""
Extended Kalman Filter for Fed-Batch Bioreactor State Estimation
================================================================
EN.625.714 Stochastic Differential Equations - Course Project

Simulates a 3-state bioreactor (VCC, glucose, titer) under Monod kinetics,
generates synthetic measurements from two online probes (capacitance, Raman)
and sparse offline assays, then runs an EKF to recover the true state.

Author: Zach Hatzenbeller
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# ============================================================================
# 1. PROCESS MODEL PARAMETERS
# ============================================================================

@dataclass
class BioprocessParams:
    """Kinetic and operational parameters for the fed-batch bioreactor."""
    # Monod kinetics
    mu_max: float = 0.035      # max specific growth rate [1/hr]
    K_s: float = 0.5           # Monod half-saturation constant [g/L]
    k_d: float = 0.003         # cell death rate [1/hr]

    # Yield and maintenance
    Y_xs: float = 2.5          # biomass yield on substrate [cells/g]
    m_s: float = 0.005         # maintenance coefficient [g/g/hr]

    # Product formation
    q_p: float = 0.01          # specific productivity [g/cell/hr]

    # Feed profile (bolus feed)
    F_s_conc: float = 400.0    # feed concentration [g/L]
    feed_start: float = 48.0   # feed start time [hr]
    feed_interval: float = 24.0  # feed every 24 hrs
    feed_volume: float = 0.05  # fractional volume added per bolus

    # Reactor
    V0: float = 1.0            # initial working volume [L] (normalized)

    # Simulation
    t_final: float = 336.0     # 14-day batch [hr]

    # Initial conditions [Xv, S, P]
    x0: np.ndarray = field(default_factory=lambda: np.array([0.5, 6.0, 0.0]))


# ============================================================================
# 2. BIOREACTOR ODE SYSTEM
# ============================================================================

def monod(S: float, params: BioprocessParams) -> float:
    """Monod specific growth rate."""
    return params.mu_max * S / (params.K_s + S)


def feed_rate(t: float, params: BioprocessParams) -> float:
    """
    Bolus feed approximated as a smooth pulse every feed_interval hours,
    starting at feed_start. Returns instantaneous substrate addition rate [g/L/hr].
    """
    if t < params.feed_start:
        return 0.0

    # Time since last feed event
    t_since_feed = (t - params.feed_start) % params.feed_interval

    # Approximate bolus as a narrow Gaussian pulse (width ~1 hr)
    pulse_width = 1.0  # hr
    pulse = np.exp(-0.5 * (t_since_feed / pulse_width) ** 2)

    # Scale so that integral over one pulse ≈ feed_volume * F_s_conc
    rate = params.feed_volume * params.F_s_conc * pulse / (pulse_width * np.sqrt(2 * np.pi))
    return rate


def bioreactor_odes(t: float, x: np.ndarray, params: BioprocessParams) -> np.ndarray:
    """
    Right-hand side of the bioreactor ODE system.

    States: x = [Xv, S, P]
        Xv - viable cell concentration
        S  - substrate (glucose) concentration
        P  - product (mAb titer) concentration
    """
    Xv, S, P = x

    # Prevent negative concentrations (numerical safeguard)
    Xv = max(Xv, 0.0)
    S = max(S, 0.0)
    P = max(P, 0.0)

    mu = monod(S, params)
    F_s = feed_rate(t, params)

    dXv_dt = mu * Xv - params.k_d * Xv
    dS_dt = -(mu * Xv) / params.Y_xs - params.m_s * Xv + F_s

    # Prevent substrate from being driven further negative
    if S <= 0.0 and dS_dt < 0.0:
        dS_dt = 0.0
        # Also halt growth if no substrate
        dXv_dt = -params.k_d * Xv

    dP_dt = params.q_p * Xv

    return np.array([dXv_dt, dS_dt, dP_dt])


# ============================================================================
# 3. GROUND TRUTH SIMULATION
# ============================================================================

def simulate_ground_truth(
    params: BioprocessParams,
    dt: float = 0.5,  # integration output step [hr]
) -> dict:
    """
    Solve the bioreactor ODEs to generate the true state trajectory.

    Returns dict with 't', 'x_true' (N x 3 array), and 'params'.
    """
    t_span = (0.0, params.t_final)
    t_eval = np.arange(0.0, params.t_final + dt, dt)
 
    sol = solve_ivp(
        fun=lambda t, x: bioreactor_odes(t, x, params),
        t_span=t_span,
        y0=params.x0,
        t_eval=t_eval,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
        max_step=0.5,  # capture feed pulses accurately
    )

    if not sol.success:
        raise RuntimeError(f"ODE integration failed: {sol.message}")

    return {
        "t": sol.t,
        "x_true": sol.y.T,  # shape (N, 3)
        "params": params,
    }


# ============================================================================
# 4. MEASUREMENT GENERATION
# ============================================================================

@dataclass
class SensorConfig:
    """
    Defines the measurement model:
      - Online sensors (capacitance for Xv, Raman for S): every dt_online hours
      - Offline assays (VCC, glucose, titer): every dt_offline hours

    Measurement vector (when all available):
        z = [cap, raman, VCC_offline, gluc_offline, titer_offline]

    Proportionality constants:
        cap   = alpha * Xv + noise
        raman = beta  * S  + noise
    """
    # Online sensor parameters
    alpha: float = 1.5          # capacitance proportionality to Xv
    beta: float = 0.8           # Raman proportionality to glucose
    dt_online: float = 0.5      # online sampling interval [hr]

    # Offline assay parameters
    dt_offline: float = 24.0    # offline sampling interval [hr]

    # Measurement noise standard deviations
    sigma_cap: float = 0.6      # capacitance noise std
    sigma_raman: float = 0.5    # Raman noise std
    sigma_vcc: float = 0.15      # offline VCC noise std
    sigma_gluc: float = 0.20    # offline glucose noise std
    sigma_titer: float = 0.10   # offline titer noise std


def generate_measurements(
    sim: dict,
    sensor: SensorConfig,
    rng: Optional[np.random.Generator] = None,
) -> dict:
    """
    Generate synthetic measurements from the true trajectory.

    Returns dict with:
        'online_times', 'online_meas' (M_online x 2): [cap, raman]
        'offline_times', 'offline_meas' (M_offline x 3): [VCC, glucose, titer]
    """
    if rng is None:
        rng = np.random.default_rng(42)

    t = sim["t"]
    x_true = sim["x_true"]  # (N, 3): [Xv, S, P]

    # --- Online measurements ---
    online_idx = np.arange(0, len(t), max(1, int(sensor.dt_online / (t[1] - t[0]))))
    online_times = t[online_idx]
    Xv_true_online = x_true[online_idx, 0]
    S_true_online = x_true[online_idx, 1]

    cap_meas = sensor.alpha * Xv_true_online + rng.normal(0, sensor.sigma_cap, len(online_idx))
    raman_meas = sensor.beta * S_true_online + rng.normal(0, sensor.sigma_raman, len(online_idx))
    online_meas = np.column_stack([cap_meas, raman_meas])

    # --- Offline measurements ---
    offline_idx = np.arange(0, len(t), max(1, int(sensor.dt_offline / (t[1] - t[0]))))
    offline_times = t[offline_idx]
    Xv_true_offline = x_true[offline_idx, 0]
    S_true_offline = x_true[offline_idx, 1]
    P_true_offline = x_true[offline_idx, 2]

    vcc_meas = Xv_true_offline + rng.normal(0, sensor.sigma_vcc, len(offline_idx))
    gluc_meas = S_true_offline + rng.normal(0, sensor.sigma_gluc, len(offline_idx))
    titer_meas = P_true_offline + rng.normal(0, sensor.sigma_titer, len(offline_idx))
    offline_meas = np.column_stack([vcc_meas, gluc_meas, titer_meas])

    return {
        "online_times": online_times,
        "online_meas": online_meas,
        "offline_times": offline_times,
        "offline_meas": offline_meas,
    }


# ============================================================================
# 5. EXTENDED KALMAN FILTER
# ============================================================================

def compute_jacobian(
    x: np.ndarray, params: BioprocessParams, dt: float
) -> np.ndarray:
    """
    Analytical Jacobian F_k of the discretized state transition.

    F = I + dt * J, where J is the continuous-time Jacobian.
    See Algorithm 2 in the project outline.
    """
    Xv, S, P = x
    Xv = max(Xv, 1e-12)
    S = max(S, 1e-12)

    mu = monod(S, params)
    dmu_dS = params.mu_max * params.K_s / (params.K_s + S) ** 2

    # Continuous-time Jacobian
    J = np.array([
        [mu - params.k_d,                    dmu_dS * Xv,                  0.0],
        [-mu / params.Y_xs - params.m_s,    -dmu_dS * Xv / params.Y_xs,    0.0],
        [params.q_p,                         0.0,                          0.0],
    ])

    # First-order Euler discretization
    F = np.eye(3) + dt * J
    return F


def ekf_predict(
    x_hat: np.ndarray,
    P: np.ndarray,
    Q: np.ndarray,
    params: BioprocessParams,
    t: float,
    dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    EKF predict step: propagate state and covariance forward by dt.

    Uses RK4 for the nonlinear state propagation and the analytical
    Jacobian (Euler-discretized) for covariance propagation.
    """
    # --- RK4 state propagation ---
    def f(t_, x_):
        return bioreactor_odes(t_, x_, params)

    k1 = f(t, x_hat)
    k2 = f(t + dt / 2, x_hat + dt / 2 * k1)
    k3 = f(t + dt / 2, x_hat + dt / 2 * k2)
    k4 = f(t + dt, x_hat + dt * k3)
    x_pred = x_hat + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    # Enforce non-negativity
    x_pred = np.maximum(x_pred, 0.0)

    # --- Covariance propagation ---
    F = compute_jacobian(x_hat, params, dt)
    P_pred = F @ P @ F.T + Q

    return x_pred, P_pred


def ekf_update(
    x_pred: np.ndarray,
    P_pred: np.ndarray,
    z: np.ndarray,
    H: np.ndarray,
    R: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    EKF update step using the Joseph form for numerical stability.

    Returns updated state, covariance, and innovations vector.
    """
    # Innovation
    z_pred = H @ x_pred
    nu = z - z_pred

    # Innovation covariance
    S = H @ P_pred @ H.T + R

    # Kalman gain
    K = P_pred @ H.T @ np.linalg.inv(S)

    # State update
    x_upd = x_pred + K @ nu

    # Covariance update (Joseph form)
    I_KH = np.eye(len(x_pred)) - K @ H
    P_upd = I_KH @ P_pred @ I_KH.T + K @ R @ K.T

    return x_upd, P_upd, nu


def build_measurement_matrices(
    sensor: SensorConfig, meas_type: str
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build H and R matrices for a given measurement type.

    meas_type: 'online', 'offline', or 'both'
    """
    if meas_type == "online":
        # z = [alpha * Xv, beta * S]
        H = np.array([
            [sensor.alpha, 0.0, 0.0],
            [0.0, sensor.beta, 0.0],
        ])
        R = np.diag([sensor.sigma_cap ** 2, sensor.sigma_raman ** 2])

    elif meas_type == "offline":
        # z = [Xv, S, P]
        H = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ])
        R = np.diag([
            sensor.sigma_vcc ** 2,
            sensor.sigma_gluc ** 2,
            sensor.sigma_titer ** 2,
        ])

    elif meas_type == "both":
        # z = [alpha*Xv, beta*S, Xv, S, P]
        H = np.array([
            [sensor.alpha, 0.0, 0.0],
            [0.0, sensor.beta, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ])
        R = np.diag([
            sensor.sigma_cap ** 2,
            sensor.sigma_raman ** 2,
            sensor.sigma_vcc ** 2,
            sensor.sigma_gluc ** 2,
            sensor.sigma_titer ** 2,
        ])
    else:
        raise ValueError(f"Unknown meas_type: {meas_type}")

    return H, R


def run_ekf(
    sim: dict,
    meas: dict,
    sensor: SensorConfig,
    Q: np.ndarray,
    P0: Optional[np.ndarray] = None,
    x0_hat: Optional[np.ndarray] = None,
) -> dict:
    """
    Run the EKF over the full batch, fusing online and offline measurements.

    Returns dict with:
        't'           : time vector
        'x_hat'       : state estimates (N x 3)
        'P_hist'      : covariance diagonal history (N x 3)
        'innovations'  : list of (time, nu, S_innov) tuples for diagnostics
    """
    params = sim["params"]
    t = sim["t"]
    dt = t[1] - t[0]
    N = len(t)

    # Initial estimate (slightly perturbed from true initial condition)
    if x0_hat is None:
        x0_hat = params.x0 * np.array([0.8, 1.2, 0.0])  # intentional offset
        x0_hat[2] = 0.0  # titer starts at 0 regardless
    if P0 is None:
        P0 = np.diag([0.1, 1.0, 0.01])

    # Pre-index measurement times into sets for O(1) lookup
    # Build dicts mapping rounded time -> index for fast access
    online_time_to_idx = {}
    for i, t_on in enumerate(meas["online_times"]):
        online_time_to_idx[round(t_on, 4)] = i

    offline_time_to_idx = {}
    for i, t_off in enumerate(meas["offline_times"]):
        offline_time_to_idx[round(t_off, 4)] = i

    # Build measurement matrices
    H_online, R_online = build_measurement_matrices(sensor, "online")
    H_offline, R_offline = build_measurement_matrices(sensor, "offline")
    H_both, R_both = build_measurement_matrices(sensor, "both")

    # Storage
    x_hat_hist = np.zeros((N, 3))
    P_diag_hist = np.zeros((N, 3))
    innovations_log = []

    x_hat = x0_hat.copy()
    P = P0.copy()
    x_hat_hist[0] = x_hat
    P_diag_hist[0] = np.diag(P)

    for k in range(1, N):
        t_k = t[k]
        t_k_round = round(t_k, 4)

        # --- Predict ---
        x_hat, P = ekf_predict(x_hat, P, Q, params, t[k - 1], dt)

        # --- Determine which measurements are available ---
        online_idx = online_time_to_idx.get(t_k_round)
        offline_idx = offline_time_to_idx.get(t_k_round)

        has_online = online_idx is not None
        has_offline = offline_idx is not None

        # --- Update ---
        if has_online and has_offline:
            z = np.concatenate([
                meas["online_meas"][online_idx],
                meas["offline_meas"][offline_idx],
            ])
            x_hat, P, nu = ekf_update(x_hat, P, z, H_both, R_both)
            S_innov = H_both @ P @ H_both.T + R_both
            innovations_log.append((t_k, nu, S_innov))

        elif has_online:
            z = meas["online_meas"][online_idx]
            x_hat, P, nu = ekf_update(x_hat, P, z, H_online, R_online)
            S_innov = H_online @ P @ H_online.T + R_online
            innovations_log.append((t_k, nu, S_innov))

        elif has_offline:
            z = meas["offline_meas"][offline_idx]
            x_hat, P, nu = ekf_update(x_hat, P, z, H_offline, R_offline)
            S_innov = H_offline @ P @ H_offline.T + R_offline
            innovations_log.append((t_k, nu, S_innov))

        # Enforce non-negativity on state estimate
        x_hat = np.maximum(x_hat, 0.0)

        x_hat_hist[k] = x_hat
        P_diag_hist[k] = np.diag(P)

    return {
        "t": t,
        "x_hat": x_hat_hist,
        "P_diag": P_diag_hist,
        "innovations": innovations_log,
    }


# ============================================================================
# 6. DIAGNOSTICS: INNOVATIONS WHITENESS TEST
# ============================================================================

def innovations_diagnostics(ekf_result: dict, max_lag: int = 20) -> dict:
    """
    Compute normalized innovations and autocorrelation for whiteness testing.

    Returns dict with 'normalized_innovations', 'acf', 'ljung_box_stat', 'lb_pvalue'.
    """
    innov_list = ekf_result["innovations"]

    # Extract only the online innovations (2D) for consistent dimensionality
    online_innovations = [
        (t, nu, S) for t, nu, S in innov_list if len(nu) == 2
    ]

    if len(online_innovations) < max_lag + 10:
        print("Warning: Not enough innovations for reliable whiteness test.")
        return {}

    # Normalize innovations: nu_bar = S^{-1/2} * nu
    normalized = []
    for t_k, nu, S_innov in online_innovations:
        L = np.linalg.cholesky(S_innov)
        nu_bar = np.linalg.solve(L, nu)
        normalized.append(nu_bar)

    normalized = np.array(normalized)  # (M, 2)

    # Autocorrelation per channel
    acf = np.zeros((2, max_lag + 1))
    for ch in range(2):
        series = normalized[:, ch]
        n = len(series)
        mean = np.mean(series)
        var = np.var(series)
        for lag in range(max_lag + 1):
            if var > 1e-12:
                acf[ch, lag] = (
                    np.mean((series[: n - lag] - mean) * (series[lag:] - mean)) / var
                )

    # Ljung-Box statistic (per channel)
    n = len(normalized)
    lb_stat = np.zeros(2)
    for ch in range(2):
        lb_stat[ch] = n * (n + 2) * np.sum(
            acf[ch, 1: max_lag + 1] ** 2 / np.arange(n - 1, n - max_lag - 1, -1)
        )

    # p-value from chi-squared(max_lag)
    from scipy.stats import chi2
    lb_pvalue = 1 - chi2.cdf(lb_stat, df=max_lag)

    return {
        "normalized_innovations": normalized,
        "acf": acf,
        "ljung_box_stat": lb_stat,
        "ljung_box_pvalue": lb_pvalue,
    }


# ============================================================================
# 7. VISUALIZATION
# ============================================================================

def plot_results(
    sim: dict,
    meas: dict,
    ekf_result: dict,
    sensor: SensorConfig,
    title_suffix: str = "",
    save_path: Optional[str] = None,
):
    """Plot true states, measurements, and EKF estimates with ±2 sigma bounds."""

    t = sim["t"]
    x_true = sim["x_true"]
    t_hat = ekf_result["t"]
    x_hat = ekf_result["x_hat"]
    P_diag = ekf_result["P_diag"]

    state_names = [
        r"Viable Cell Conc. $X_v$",
        r"Glucose $S$",
        r"Titer $P$",
    ]
    state_units = ["[x10^6 cells/mL]", "[g/L]", "[g/L]"]

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle(
        f"EKF State Estimation — Fed-Batch Bioreactor{title_suffix}",
        fontsize=14,
        fontweight="bold",
    )

    for i, ax in enumerate(axes):
        # True trajectory
        ax.plot(t, x_true[:, i], "k-", linewidth=1.5, label="True state", zorder=3)

        # EKF estimate
        ax.plot(
            t_hat, x_hat[:, i], "b-", linewidth=1.2, label="EKF estimate", zorder=2
        )

        # ±2 sigma confidence bounds
        sigma = np.sqrt(P_diag[:, i])
        ax.fill_between(
            t_hat,
            x_hat[:, i] - 2 * sigma,
            x_hat[:, i] + 2 * sigma,
            alpha=0.5,
            color="blue",
            label=r"$\pm 2\sigma$",
        )

        # Online measurements (scaled back to state space)
        if i == 0:  # Xv: capacitance / alpha
            ax.scatter(
                meas["online_times"],
                meas["online_meas"][:, 0] / sensor.alpha,
                s=4, c="magenta", alpha=0.8, label="Online (cap/α)", zorder=1,
            )
        elif i == 1:  # S: Raman / beta
            ax.scatter(
                meas["online_times"],
                meas["online_meas"][:, 1] / sensor.beta,
                s=4, c="green", alpha=0.8, label="Online (Raman/β)", zorder=1,
            )

        # Offline measurements
        if i < 3:
            ax.scatter(
                meas["offline_times"],
                meas["offline_meas"][:, i],
                s=40, c="red", marker="x", linewidths=1.5,
                label="Offline assay", zorder=4,
            )

        ax.set_ylabel(f"{state_names[i]} {state_units[i]}")
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.5)

    axes[-1].set_xlabel("Time [hr]")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Figure saved to {save_path}")
    plt.close()


def plot_innovations(
    diag: dict,
    save_path: Optional[str] = None,
):
    """Plot normalized innovations and autocorrelation function."""
    if not diag:
        print("No diagnostics to plot.")
        return

    normalized = diag["normalized_innovations"]
    acf = diag["acf"]
    lb_stat = diag["ljung_box_stat"]
    lb_pval = diag["ljung_box_pvalue"]

    channel_names = ["Capacitance", "Raman"]

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle("Innovations Diagnostics (Martingale Whiteness Test)", fontsize=13, fontweight="bold")

    for ch in range(2):
        # Time series of normalized innovations
        ax = axes[ch, 0]
        ax.plot(normalized[:, ch], "b-", linewidth=0.5, alpha=0.7)
        ax.axhline(0, color="k", linewidth=0.5)
        ax.axhline(2, color="r", linewidth=0.5, linestyle="--", alpha=0.5)
        ax.axhline(-2, color="r", linewidth=0.5, linestyle="--", alpha=0.5)
        ax.set_title(f"{channel_names[ch]} — Normalized Innovations")
        ax.set_ylabel(r"$\bar{\nu}_k$")
        ax.set_xlabel("Measurement index")
        ax.grid(True, alpha=0.3)

        # ACF
        ax2 = axes[ch, 1]
        lags = np.arange(len(acf[ch]))
        ax2.bar(lags, acf[ch], width=0.6, color="steelblue", edgecolor="navy", linewidth=0.5)
        # 95% confidence bounds for white noise
        n = len(normalized)
        ax2.axhline(1.96 / np.sqrt(n), color="r", linestyle="--", linewidth=0.8)
        ax2.axhline(-1.96 / np.sqrt(n), color="r", linestyle="--", linewidth=0.8)
        ax2.set_title(
            f"{channel_names[ch]} — ACF  "
            f"(LB stat={lb_stat[ch]:.1f}, p={lb_pval[ch]:.3f})"
        )
        ax2.set_ylabel("Autocorrelation")
        ax2.set_xlabel("Lag")
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Figure saved to {save_path}")
    plt.close()


# ============================================================================
# 8. NOISE REGIME SWEEP
# ============================================================================

def noise_regime_sweep(
    sim: dict,
    sensor: SensorConfig,
    Q_scales: list[float],
    rng: Optional[np.random.Generator] = None,
    save_dir: str = ".",
) -> dict:
    """
    Run the EKF across multiple process noise levels (Q scaled by a factor).
    Returns RMSE for each state and each Q scale.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    meas = generate_measurements(sim, sensor, rng)
    results = {}

    for q_scale in Q_scales:
        Q = np.diag([0.001 * q_scale, 0.01 * q_scale, 0.0001 * q_scale])

        ekf_result = run_ekf(sim, meas, sensor, Q)

        # RMSE per state
        errors = sim["x_true"] - ekf_result["x_hat"]
        rmse = np.sqrt(np.mean(errors ** 2, axis=0))

        results[q_scale] = {
            "rmse": rmse,
            "ekf_result": ekf_result,
        }

        print(f"Q scale={q_scale:6.2f} | RMSE: Xv={rmse[0]:.4f}, S={rmse[1]:.4f}, P={rmse[2]:.4f}")

    return {"results": results, "meas": meas}


# ============================================================================
# 9. MAIN: RUN EVERYTHING
# ============================================================================

def main():
    print("=" * 70)
    print("Fed-Batch Bioreactor EKF Simulation")
    print("=" * 70)

    # --- Setup ---
    params = BioprocessParams()
    sensor = SensorConfig()
    rng = np.random.default_rng(42)
    figure_path = Path.cwd() / "Introductory Stochastic Differential Equations" / "Course Project" / "figures"

    # --- Simulate ground truth ---
    print("\n[1] Generating ground truth trajectory...")
    sim = simulate_ground_truth(params, dt=0.5)
    print(f"    Simulated {len(sim['t'])} time steps over {params.t_final:.0f} hrs")
    print(f"    Final state: Xv={sim['x_true'][-1, 0]:.3f}, "
          f"S={sim['x_true'][-1, 1]:.3f}, P={sim['x_true'][-1, 2]:.3f}")

    # --- Generate measurements ---
    print("\n[2] Generating synthetic measurements...")
    meas = generate_measurements(sim, sensor, rng)
    print(f"    Online measurements: {len(meas['online_times'])} samples")
    print(f"    Offline measurements: {len(meas['offline_times'])} samples")

    # --- Run EKF (baseline noise) ---
    print("\n[3] Running EKF (baseline noise)...")
    Q_baseline = np.diag([0.001, 0.01, 0.0001])
    ekf_result = run_ekf(sim, meas, sensor, Q_baseline)

    errors = sim["x_true"] - ekf_result["x_hat"]
    rmse = np.sqrt(np.mean(errors ** 2, axis=0))
    print(f"    RMSE: Xv={rmse[0]:.4f}, S={rmse[1]:.4f}, P={rmse[2]:.4f}")

    # --- Plot ---
    print("\n[4] Generating plots...")
    plot_results(sim, meas, ekf_result, sensor, save_path=figure_path / "ekf_baseline.png")

    # --- Innovations diagnostics ---
    print("\n[5] Running innovations diagnostics...")
    diag = innovations_diagnostics(ekf_result, max_lag=20)
    if diag:
        for ch, name in enumerate(["Capacitance", "Raman"]):
            print(f"    {name}: Ljung-Box stat={diag['ljung_box_stat'][ch]:.2f}, "
                  f"p-value={diag['ljung_box_pvalue'][ch]:.4f}")
    plot_innovations(diag, save_path=figure_path / "innovations_diagnostics.png")

    # --- Noise regime sweep ---
    print("\n[6] Running noise regime sweep...")
    Q_scales = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    sweep = noise_regime_sweep(sim, sensor, Q_scales, rng)

    # Plot RMSE vs Q scale
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    rmse_arr = np.array([sweep["results"][qs]["rmse"] for qs in Q_scales])
    for i, (name, marker) in enumerate(
        zip([r"$X_v$ (VCC)", r"$S$ (Glucose)", r"$P$ (Titer)"], ["o", "s", "^"])
    ):
        ax.plot(Q_scales, rmse_arr[:, i], f"-{marker}", linewidth=1.5, markersize=7, label=name)
    ax.set_xlabel("Process Noise Scale Factor", fontsize=12)
    ax.set_ylabel("RMSE", fontsize=12)
    ax.set_title("EKF Estimation Error vs. Process Noise Intensity", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.set_xscale("log")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(figure_path / "noise_sweep.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("    Saved noise_sweep.png")

    print("\n" + "=" * 70)
    print("Done. Output files: ekf_baseline.png, innovations_diagnostics.png")
    print("=" * 70)

    return sim, meas, ekf_result, diag, sweep


if __name__ == "__main__":
    sim, meas, ekf_result, diag, sweep = main()
