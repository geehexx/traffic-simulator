## 2D Python Traffic Simulation Spec (v0.4)

Date: 2025-09-20

### 1) Purpose and scope
- Simulate multi-vehicle traffic on a stadium-shaped loop to study interactions between vehicle performance, driver behavior, and road geometry.
- All visuals scale to the window; deterministic replays supported; optional accelerated runs up to 10×.
- Geometry is not constrained by safety; instead, a safety panel computes and displays safe-curve information and warnings.

### 2) Libraries and stack
- Rendering/UI: `arcade`
- Collision/impulse response for crash visuals: `pymunk`
- Data/analytics: standard Python stack (e.g., `numpy`, `collections`, CSV writing)

### 3) Geometry: stadium track and safety panel
- Stadium shape: two straights and two semicircles.
  - Let total track length be L (meters) and straight fraction be r (unitless, default r=0.30).
  - Radius of each semicircle: \( R = \frac{L(1 - r)}{2\pi} \)
  - Length of each straight: \( S = \frac{rL}{2} \)
- Safety computations (display only; do not change geometry):
  - Given design speed \( V \) in km/h, superelevation \( e \) (m/m), and side-friction factor \( f \) (unitless), the minimum safe radius is:
    \[ R_{\min} = \frac{V^2}{127\,(e + f)} \]
  - Given actual radius \( R \), the safe speed is:
    \[ V_{\text{safe}} = \sqrt{127\,R\,(e + f)} \]\(\text{ km/h}\)
  - Holding the straight fraction r constant, the total length needed to achieve \( R_{\min} \) is:
    \[ L_{\text{needed}} = \frac{2\pi R_{\min}}{1 - r} \]
- Warning message (shown only when \( R < R_{\min} \)):
  - "Unsafe curve of <x m>. Decrease speed to <y km/h> or increase track length to <z m>."
  - x = current \( R \) (rounded), y = \( V_{\text{safe}}(R) \) using chosen \( e, f \), z = \( L_{\text{needed}}(V, e, f, r) \).
- Defaults for warnings: \( e = 0.08 \), \( f = 0.10 \). Source: TxDOT/AASHTO-aligned guidance on curve radius vs design speed and superelevation (see References).

### 4) Vehicles
- Types: Sedan, SUV, Truck (light-duty), Motorbike, Bus, Van. 20 vehicles by default; random colors.
- Example subtypes (last ~20 years):
  - Sedan: Toyota Camry, Honda Accord, Ford Fusion
  - SUV: Ford Explorer, Toyota Highlander, Honda CR‑V
  - Truck (LD): Ford F‑150, Chevrolet Silverado 1500, Ram 1500
  - Motorbike: Harley‑Davidson Sportster, Yamaha YZF‑R6, Honda CBR600RR
  - Bus: Blue Bird All American, Thomas Saf‑T‑Liner, IC Bus CE
  - Van: Ford Transit, Mercedes‑Benz Sprinter, Ram ProMaster
- Attributes (SI units): mass (kg), length (m), width (m), wheelbase (m), power (kW), torque (Nm), drag area CdA (m²), tire friction \( \mu \), brake efficiency \( \eta \), comfortable decel \( b_{\text{comf}} \) (m/s²), max decel \( b_{\max} \) (m/s²), acceleration curve \( a_{\max}(v) \).
- Default composition (configurable): 55% sedan, 25% SUV, 10% truck/van, 5% bus, 5% motorbike.

### 5) Drivers: statistical model with bell-curve distributions
- We generate driver parameters from correlated, truncated normal distributions (Gaussian copula), ensuring realistic covariation.
- Core parameters (defaults; clamped to ranges):
  - Reaction time \( t_r \sim \mathcal{N}(2.5, 0.6) \) s → [0.8, 4.0]
  - Desired headway \( T \sim \mathcal{N}(1.6, 0.5) \) s → [0.6, 3.0]
  - Aggression A \( \sim \mathcal{N}(0,1) \) (latent)
  - Rule adherence R = sigmoid(latent) ∈ [0, 1]
  - Comfortable decel \( b_{\text{comf}} \sim \mathcal{N}(2.5, 0.7) \) m/s² → [1.0, 4.0]
  - Maximum decel \( b_{\max} \sim \mathcal{N}(7.0, 1.0) \) m/s² → [4.0, 9.0], capped by \( \eta\,\mu\,g \)
  - Jerk limit \( j_{\max} \sim \mathcal{N}(4.0, 1.0) \) m/s³ → [1.0, 7.0]
  - Drivetrain lags: \( \tau_{\text{throttle}} \sim \mathcal{N}(0.25, 0.10) \) s (≥0.05), \( \tau_{\text{brake}} \sim \mathcal{N}(0.15, 0.07) \) s (≥0.05)
- Example correlations:
  - Corr(A, T) = −0.5, Corr(A, \( b_{\text{comf}} \)) = +0.3, Corr(R, A) = −0.4, Corr(distraction, \( t_r \)) = +0.5

#### Speeding realism: frequency and duration
- Two-state Markov chain (Compliant ↔ Speeding):
  - Let percent-time speeding be \( p \) and mean speeding episode duration be \( D \). Then rates are \( \lambda_{\text{off}} = 1/D \) and \( \lambda_{\text{on}} = \frac{p}{1-p}\,\lambda_{\text{off}} \).
  - Targets depend on Aggression A and Rule adherence R (e.g., cautious vs baseline vs aggressive). Overspeed magnitude (km/h over limit) \( \sim \mathcal{N}(\mu=5 + 4\cdot\max(A,0), \sigma=3) \) clamped to [0, 25] and reduced by R.
- Motivation: speeding is a major crash factor and correlates with higher acceleration variance (see References: NHTSA; peer-reviewed study).

### 6) Longitudinal dynamics and actuation
- Baseline controller: Intelligent Driver Model (IDM) [Treiber & Kesting].
  - \( a = a_{\max}\left[1 - (v/v_0)^\delta - (s^*/s)^2 \right] \)
  - \( s^* = s_0 + v\,T + \frac{v\,\Delta v}{2\sqrt{a_{\max} b_{\text{comf}}}} \)
- Realism constraints:
  - Jerk limiting: \( \dot a \in [-j_{\max}, +j_{\max}] \)
  - Drivetrain lags: first-order filters with time constants \( \tau_{\text{throttle}} \), \( \tau_{\text{brake}} \)
  - Physical clamp: \( a \ge -\eta\,\mu\,g \)

### 7) Perception and SSD (daytime, occlusion-aware)
- Drivers only react to the first unobstructed leader in-lane within visual range.
- Dynamic SSD generalized to leader–follower kinematics:
  - Reaction distance: \( d_r = v_f \cdot t_r \)
  - Required gap to avoid collision under braking:
    \[ g_{\text{req}} = \max\!\left(s_0,\ d_r + \frac{v_f^2}{2 b_f} - \frac{v_\ell^2}{2 b_\ell} \right) \]
  - Here \( v_f \) and \( v_\ell \) are follower/leader speeds (m/s); \( b_f, b_\ell \) are expected decelerations; \( s_0 \) is a standstill buffer.

### 8) Collisions and recovery
- Detection: 1D ordering along centerline with AABB overlap check.
- Response: brief `pymunk` impulse to push sideways/rotate; then vehicle is temporarily disabled for 5 s (no throttle). Visual blink during disable.
- Logged at impact: time, involved IDs, location (arc length), Δv, TTC-at-impact.

### 9) Rendering, timing, determinism
- Fixed-step physics (e.g., Δt = 0.02 s) with accumulator; rendering interpolates between states.
- Deterministic given fixed random seed(s). Speed factor up to 10× via multiple fixed substeps per frame while keeping Δt constant.
- Performance: pre-sort vehicles by arc length each tick (or maintain order with minimal swaps), cache occlusion relationships, vectorize state updates, use branchless clamps, prefer float32 where acceptable, and introduce fast approximations (e.g., cached inverse sqrt) only if profiling indicates benefit.

Implementation note (current): using Arcade 3.3.x, rotated vehicle rectangles are rendered via `draw_polygon_filled` for compatibility.

### 10) HUD and analytics
- Minimal HUD (default):
  - Speed histogram (km/h) with mean/percentiles
  - Headway summary (median; share < 1.0 s)
  - Near-miss counter (TTC < 1.5 s)
  - Safe-curve panel: display R, \( V_{\text{safe}} \), \( L_{\text{needed}} \), and the warning if unsafe
- Full HUD (toggle):
  - TTC histogram
  - Braking heatmap vs arc length
  - Per-vehicle overlays (speed, accel, jerk, SSD, occlusion flag)
  - Incident log with Δv and location

### 11) Configuration (restart to apply)
- Stored in `config/config.yaml`. Key groups:
  - `track`: `length_m`, `straight_fraction`, `superelevation_e`, `side_friction_f`, `safety_design_speed_kmh`, `speed_limit_kmh`
  - `vehicles`: `count`, `mix`, `color_random_seed`
  - `drivers`: parameter distributions, bounds, correlations; overspeed model (percent-time and episode duration targets, overspeed magnitude)
  - `physics`: `delta_t_s`, `speed_factor`, `gravity_mps2`, `tire_friction_mu`, `brake_efficiency_eta`
  - `render`: `target_fps`, HUD mode/toggle, effects
  - `collisions`: impulse on/off, disable time, lateral push
  - `random`: master seed (optional)
  - `logging`: aggregate rates, per-vehicle trace rate, rolling window, debug toggle/rate, output path

### 12) Acceptance criteria (v0)
- Window resizes maintain scaling; ≥ 30 FPS on target hardware.
- 20 vehicles circulate stably with realistic spacing; statistical drivers produce measurable differences (headway, braking onset, overspeeding percent-time and episode durations).
- Occlusion-based perception with dynamic SSD active.
- Safety panel displays R, \( V_{\text{safe}} \), and \( L_{\text{needed}} \); warning appears when unsafe.
- Deterministic replay under fixed seed; up to 10× speed factor stable.
- Collisions create visual effect and disable the vehicle for 5 s.

### 13) Variable and unit glossary
- Geometry: L, R, S in meters; r unitless; e (m/m); f unitless.
- Speeds: V (km/h) in formulas above; v, \( v_f \), \( v_\ell \) in m/s.
- Dynamics: \( a \) (m/s²), \( j \) (m/s³), \( b_{\text{comf}} \), \( b_{\max} \) (m/s²), \( T \) (s), \( t_r \) (s), \( s_0 \) (m).

### 14) References
- Curve radius vs design speed and superelevation (AASHTO-aligned): TxDOT, “Curve Radius” — `txdot.gov`
- Stopping Sight Distance (SSD) formulation and design reaction time: AASHTO “Green Book” (2018)
- Speeding prevalence and safety impact: NHTSA “Speeding” (2023) — `nhtsa.gov`
- Aggressive driving correlation with acceleration variance and overspeeding: peer-reviewed study — `pmc.ncbi.nlm.nih.gov`
- Car-following: Treiber & Kesting, Traffic Flow Dynamics, Springer, 2013


