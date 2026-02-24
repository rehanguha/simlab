# Mathematical Derivations

This document provides complete mathematical derivations for all physics models used in the ball drop/launch simulation. All equations use SI units unless otherwise specified.

---

## Table of Contents

1. [Equations of Motion](#1-equations-of-motion)
2. [Drag Force and Coefficient](#2-drag-force-and-coefficient)
3. [Magnus Effect](#3-magnus-effect)
4. [Air Properties](#4-air-properties)
5. [Ground Contact Mechanics](#5-ground-contact-mechanics)
6. [Virtual Mass Effect](#6-virtual-mass-effect)
7. [Spin Decay](#7-spin-decay)
8. [Wind Modeling](#8-wind-modeling)
9. [Numerical Integration](#9-numerical-integration)
10. [Units Summary](#10-units-summary)

---

## 1. Equations of Motion

### 1.1 Translational Dynamics

The ball is modeled as a rigid sphere with 6 degrees of freedom (3 translational + 3 rotational). The translational equation of motion follows Newton's second law:

$$m_{eff} \frac{d\vec{v}}{dt} = \vec{F}_{drag} + \vec{F}_{Magnus} + \vec{F}_{gravity} + \vec{F}_{buoyancy}$$

Where:
- $m_{eff}$ = effective mass including virtual mass effect [kg]
- $\vec{v}$ = velocity vector [m/s]
- $\vec{F}_{drag}$ = aerodynamic drag force [N]
- $\vec{F}_{Magnus}$ = Magnus lift force [N]
- $\vec{F}_{gravity}$ = gravitational force [N]
- $\vec{F}_{buoyancy}$ = buoyancy force [N]

### 1.2 Component Form

Expanding into Cartesian components:

$$\frac{dv_x}{dt} = \frac{F_{drag,x} + F_{Magnus,x}}{m_{eff}}$$

$$\frac{dv_y}{dt} = \frac{F_{drag,y} + F_{Magnus,y}}{m_{eff}}$$

$$\frac{dv_z}{dt} = \frac{F_{drag,z} + F_{Magnus,z} - mg + F_{buoyancy}}{m_{eff}}$$

### 1.3 Rotational Dynamics

The angular velocity evolves according to:

$$I \frac{d\vec{\omega}}{dt} = \vec{\tau}_{aero} + \vec{\tau}_{contact}$$

Where $I = \frac{2}{5}mR^2$ is the moment of inertia for a solid sphere.

### 1.4 Assumptions

1. **Rigid body**: No deformation effects during flight (only during contact)
2. **Point mass approximation**: Valid when R ≪ trajectory length scale
3. **Negligible Coriolis force**: Appropriate for short-range trajectories
4. **Constant gravitational acceleration**: Valid for altitudes < 11 km

---

## 2. Drag Force and Coefficient

### 2.1 Drag Force Expression

The aerodynamic drag force on a sphere is:

$$\vec{F}_{drag} = -\frac{1}{2} \rho C_d A |\vec{v}_{rel}| \vec{v}_{rel}$$

Where:
- $\rho$ = air density [kg/m³]
- $C_d$ = drag coefficient [dimensionless]
- $A = \pi R^2$ = cross-sectional area [m²]
- $\vec{v}_{rel} = \vec{v} - \vec{w}$ = velocity relative to air [m/s]
- $\vec{w}$ = wind velocity [m/s]

### 2.2 Reynolds Number

The Reynolds number characterizes the flow regime:

$$Re = \frac{2R |\vec{v}_{rel}|}{\nu} = \frac{2R |\vec{v}_{rel}| \rho}{\mu}$$

Where:
- $\nu = \mu/\rho$ = kinematic viscosity [m²/s]
- $\mu$ = dynamic viscosity [Pa·s]

### 2.3 Multi-Regime Drag Coefficient

The simulation uses a piecewise drag correlation spanning all flow regimes:

#### Regime 1: Stokes Flow (Re ≤ 1)

$$C_d = \frac{24}{Re}$$

This is the analytical solution for creeping flow with no separation.

#### Regime 2: Schiller-Naumann Correlation (1 < Re ≤ 1000)

$$C_d = \frac{24}{Re}(1 + 0.15 Re^{0.687})$$

An empirical correlation accounting for inertial effects.

#### Regime 3: Newton Regime (1000 < Re ≤ 3×10⁵)

$$C_d = 0.44 + \left(\frac{0.42}{1 + 42500/Re^{1.16}} - 0.44\right) \exp\left(-\frac{Re - 1000}{500}\right)$$

Approximately constant $C_d ≈ 0.44$ with boundary layer effects.

#### Regime 4: Drag Crisis (3×10⁵ < Re ≤ 3.5×10⁵)

$$C_d = 0.44 - 0.35 \sqrt{\frac{Re - 3×10^5}{5×10^4}}$$

The drag crisis occurs when the boundary layer transitions from laminar to turbulent, causing delayed separation and reduced wake.

#### Regime 5: Post-Crisis (Re > 3.5×10⁵)

$$C_d = 0.09 + 0.06 \exp\left(-\frac{Re - 3.5×10^5}{10^6}\right)$$

Gradual recovery toward $C_d ≈ 0.1-0.2$.

### 2.4 Compressibility Correction

For Mach number $Ma > 0.3$:

$$C_d = C_d^{incomp} (1 + 0.15 Ma^2)$$

For $Ma > 0.8$:

$$C_d = C_d^{incomp} (1 + 0.15 Ma^2) (1 + 0.5(Ma - 0.8)^2)$$

### 2.5 Surface Roughness Effect

Surface roughness shifts the drag crisis to lower Reynolds numbers:

$$Re_{crit} = Re_{crit}^{smooth} (1 - 0.5 r_f)$$

Where $r_f = \min(\varepsilon \times 10^4, 0.8)$ and $\varepsilon$ is the roughness height in meters.

---

## 3. Magnus Effect

### 3.1 Physical Mechanism

The Magnus effect arises from asymmetric boundary layer separation due to rotation. On the side rotating with the flow, the boundary layer separates later, creating a pressure differential.

### 3.2 Magnus Force

$$\vec{F}_{Magnus} = \frac{1}{2} \rho C_L A |\vec{v}_{rel}|^2 \hat{n}_{lift}$$

Where the lift direction is:

$$\hat{n}_{lift} = \frac{\vec{\omega} \times \vec{v}_{rel}}{|\vec{\omega} \times \vec{v}_{rel}|}$$

### 3.3 Lift Coefficient (Mehta Correlation)

The simulation uses the Mehta correlation:

$$C_L = \frac{0.4 S}{1 + 2S} \cdot f(Re) \cdot f(\varepsilon)$$

Where the spin parameter is:

$$S = \frac{\omega R}{|\vec{v}_{rel}|}$$

The Reynolds number correction:

$$f(Re) = \begin{cases} Re/10^4 & Re < 10^4 \\ 1 + 0.1 \log_{10}(Re/10^6) & Re > 10^6 \\ 1 & \text{otherwise} \end{cases}$$

The roughness correction:

$$f(\varepsilon) = 1 + 0.2 \min(\varepsilon \times 10^3, 1)$$

### 3.4 Lift Coefficient Limit

The lift coefficient is capped at $C_L \leq 0.8$ to prevent unphysical results at extreme spin rates.

---

## 4. Air Properties

### 4.1 International Standard Atmosphere (ISA)

The ISA model defines temperature and pressure variation with altitude:

**Temperature** (troposphere, z < 11 km):

$$T(z) = T_0 - L z$$

Where:
- $T_0 = 288.15$ K (15°C)
- $L = 0.0065$ K/m (lapse rate)

**Pressure**:

$$p(z) = p_0 \left(\frac{T(z)}{T_0}\right)^{g/(R L)}$$

Where:
- $p_0 = 101325$ Pa
- $R = 287.058$ J/(kg·K) (specific gas constant for dry air)

### 4.2 Density from Ideal Gas Law

For dry air:

$$\rho = \frac{p}{R T}$$

### 4.3 Humidity Correction

Water vapor is less dense than dry air. The corrected density uses:

$$\rho = \frac{p_d}{R_d T} + \frac{e}{R_v T}$$

Where:
- $p_d$ = partial pressure of dry air
- $e$ = partial pressure of water vapor
- $R_d = 287.058$ J/(kg·K)
- $R_v = 461.495$ J/(kg·K)

The saturation vapor pressure (Buck equation):

$$e_s = 611.21 \exp\left(\frac{(18.678 - T_c/234.5) T_c}{257.14 + T_c}\right)$$

Where $T_c$ is temperature in Celsius.

The actual vapor pressure:

$$e = e_s \cdot \frac{RH}{100}$$

### 4.4 Dynamic Viscosity (Sutherland's Law)

$$\mu = \mu_{ref} \left(\frac{T}{T_{ref}}\right)^{3/2} \frac{T_{ref} + S}{T + S}$$

Where:
- $\mu_{ref} = 1.716 \times 10^{-5}$ Pa·s
- $T_{ref} = 273.15$ K
- $S = 111$ K (Sutherland constant)

### 4.5 Humidity Correction for Viscosity

$$\mu_{wet} = \mu_{dry} (1 - 0.0004 \cdot RH/100)$$

A small correction accounting for water vapor's lower viscosity.

### 4.6 Speed of Sound

$$c = \sqrt{\gamma R T}$$

Where $\gamma = 1.4$ for air.

With humidity correction:

$$c = \sqrt{\gamma_m R_m T}$$

Where:
- $R_m = R (1 - 0.378 x_v)$
- $\gamma_m = \gamma (1 - 0.1 x_v)$
- $x_v = e/p$ (mole fraction of water vapor)

### 4.7 Mach Number

$$Ma = \frac{|\vec{v}_{rel}|}{c}$$

---

## 5. Ground Contact Mechanics

### 5.1 Collision Detection

Collision occurs when:

$$z - R \leq z_{ground}(x, y)$$

Where $z_{ground}$ is the surface height function.

### 5.2 Surface Geometry

**Height function**:

$$z_{ground}(x,y) = h_0 + s_x x + s_y y + a_r \sin\left(\frac{2\pi x}{\lambda_x}\right) \sin\left(\frac{2\pi y}{\lambda_y}\right)$$

Where:
- $h_0$ = base height [m]
- $s_x, s_y$ = slopes [dimensionless]
- $a_r$ = roughness amplitude [m]
- $\lambda_x, \lambda_y$ = roughness wavelengths [m]

**Surface normal**:

$$\hat{n} = \frac{(-\partial z/\partial x, -\partial z/\partial y, 1)}{|(-\partial z/\partial x, -\partial z/\partial y, 1)|}$$

### 5.3 Contact Velocity

The velocity at the contact point includes both translation and rotation:

$$\vec{v}_c = \vec{v} + \vec{\omega} \times \vec{r}$$

Where $\vec{r} = -R \hat{n}$ is the vector from center to contact point.

### 5.4 Normal and Tangential Components

**Normal velocity**:

$$v_n = \vec{v}_c \cdot \hat{n}$$

**Tangential velocity**:

$$\vec{v}_t = \vec{v}_c - v_n \hat{n}$$

$$v_t = |\vec{v}_t|$$

### 5.5 Coefficient of Restitution

#### Hertzian Contact Model

The coefficient of restitution decreases with impact velocity:

$$e(v_n) = e_{ref} \exp\left(-k_m \ln\left(\frac{|v_n|}{v_{ref}}\right)\right)$$

Where:
- $e_{ref}$ = reference coefficient at $v_{ref}$
- $v_{ref} = 1$ m/s (reference velocity)
- $k_m$ = material parameter (typically 0.02-0.05)

For low velocities:

$$e(v_n) = e_{ref} \left(1 - 0.1 \frac{v_{ref} - |v_n|}{v_{ref}}\right)$$

#### Environmental Corrections

$$e_{eff} = e(v_n) (1 - dampness)$$

Wetness reduces friction and restitution:

$$e_{wet} = e_{eff} (1 - 0.5 \times wetness)$$

### 5.6 Impulse Calculation

**Normal impulse**:

$$J_n = -(1 + e) m v_n$$

**Tangential impulse** (Coulomb friction model):

First, calculate the impulse for sticking:

$$J_t^* = m_{eff,c} v_t$$

Where $m_{eff,c} = m / (1 + I/(mR^2))$ is the effective mass for tangential motion.

If $J_t^* \leq \mu_s |J_n|$: **sticking**
$$\vec{J}_t = -J_t^* \hat{t}$$

If $J_t^* > \mu_s |J_n|$: **sliding**
$$\vec{J}_t = -\mu_k |J_n| \hat{t}$$

Where $\hat{t} = \vec{v}_t / v_t$ is the tangent direction.

### 5.7 Post-Collision Velocities

**Linear velocity**:

$$\vec{v}' = \vec{v} + \frac{J_n}{m} \hat{n} + \frac{\vec{J}_t}{m}$$

**Angular velocity**:

$$\vec{\omega}' = \vec{\omega} + \frac{\vec{r} \times \vec{J}_t}{I}$$

### 5.8 Rolling Resistance

After contact, rolling resistance reduces tangential motion:

$$\vec{v}_{plane}' = \vec{v} - (\vec{v} \cdot \hat{n}) \hat{n}$$

$$\Delta v = \min(c_{rr} g \Delta t, |\vec{v}_{plane}|)$$

Where $c_{rr} = 0.02 + 0.08 \times wetness$.

---

## 6. Virtual Mass Effect

### 6.1 Physical Origin

When a sphere accelerates through a fluid, it must also accelerate the surrounding fluid. This creates an "added mass" effect.

### 6.2 Added Mass

For a sphere:

$$m_{added} = C_m \rho V$$

Where:
- $C_m = 1/2$ for a sphere
- $V = \frac{4}{3}\pi R^3$ is the volume

### 6.3 Effective Mass

$$m_{eff} = m + m_{added} = m + \frac{1}{2} \rho V$$

This effective mass is used in the equations of motion during acceleration phases.

---

## 7. Spin Decay

### 7.1 Mechanisms

Spin decays due to:
1. **Aerodynamic torque**: Viscous shear on the rotating surface
2. **Surface friction**: During ground contact

### 7.2 Aerodynamic Torque Coefficient

$$C_T(Re, S) = \begin{cases} \frac{64\pi}{Re + 1} & Re < 1 \\ \frac{0.5}{Re^{0.3}}(1 + S) & Re < 1000 \\ 0.05(1 + 0.5S) & Re \geq 1000 \end{cases}$$

### 7.3 Torque

$$\tau_{aero} = \frac{1}{2} \rho |\vec{v}_{rel}|^2 R A C_T$$

### 7.4 Angular Deceleration

$$\frac{d|\vec{\omega}|}{dt} = -\frac{\tau_{aero}}{I}$$

### 7.5 Additional Decay

A simplified decay model adds:

$$\frac{d\vec{\omega}}{dt} = -(c_{decay} + c_{aero} |\vec{v}_{rel}|) \vec{\omega}$$

---

## 8. Wind Modeling

### 8.1 Mean Wind Profile (Power Law)

$$\bar{w}(z) = w_{ref} \left(\frac{z}{z_{ref}}\right)^\alpha$$

Where:
- $w_{ref}$ = reference wind speed at $z_{ref}$
- $\alpha$ = power law exponent (0.12-0.16 for open terrain)

### 8.2 Wind Direction

$$\vec{w}_{mean} = \bar{w}(z) (\cos\psi, \sin\psi, 0)$$

Where $\psi$ is the wind direction angle.

### 8.3 Gust Modeling (Ornstein-Uhlenbeck Process)

Gusts are modeled as a correlated random process:

$$dx = -\frac{x}{\tau} dt + \sigma \sqrt{\frac{2}{\tau}} dW$$

Where:
- $\tau$ = correlation time [s]
- $\sigma$ = gust intensity [m/s]
- $dW$ = Wiener process increment

The discrete update:

$$x_{n+1} = x_n - \frac{x_n}{\tau} \Delta t + \sigma \sqrt{\frac{2\Delta t}{\tau}} \xi$$

Where $\xi \sim \mathcal{N}(0,1)$.

### 8.4 Total Wind

$$\vec{w} = \vec{w}_{mean} + \vec{w}_{gust}$$

---

## 9. Numerical Integration

### 9.1 Fixed Timestep (Euler Method)

$$\vec{y}_{n+1} = \vec{y}_n + \Delta t \cdot f(\vec{y}_n)$$

Simple but requires small timesteps for accuracy.

### 9.2 Adaptive Timestep (RK45 Dormand-Prince)

The method computes both 4th and 5th order solutions:

$$\vec{y}_{n+1}^{(4)} = \vec{y}_n + \Delta t \sum_{i=1}^{7} b_i^{(4)} k_i$$

$$\vec{y}_{n+1}^{(5)} = \vec{y}_n + \Delta t \sum_{i=1}^{7} b_i^{(5)} k_i$$

Where $k_i$ are stage derivatives.

**Error estimate**:

$$err = \max_i \frac{|y_{n+1,i}^{(5)} - y_{n+1,i}^{(4)}|}{atol + rtol \cdot \max(|y_{n,i}|, |y_{n+1,i}^{(5)}|)}$$

**Timestep adjustment**:

$$\Delta t_{new} = \Delta t \cdot \min(5, \max(0.1, 0.9 \cdot err^{-0.2}))$$

### 9.3 Stability Monitoring

**NaN/Inf detection**: Flag if any state variable becomes non-finite.

**Energy monitoring**: Track total mechanical energy:

$$E = \frac{1}{2}m|\vec{v}|^2 + mgz + \frac{1}{2}I|\vec{\omega}|^2$$

Energy gains > 50% indicate numerical instability.

---

## 10. Units Summary

| Quantity | Symbol | SI Unit | Typical Range |
|----------|--------|---------|---------------|
| Mass | m | kg | 0.05 - 1.0 |
| Radius | R | m | 0.02 - 0.15 |
| Velocity | v | m/s | 0 - 100 |
| Angular velocity | ω | rad/s | 0 - 1000 |
| Time | t | s | 0 - 100 |
| Position | x, y, z | m | - |
| Air density | ρ | kg/m³ | 0.9 - 1.3 |
| Dynamic viscosity | μ | Pa·s | 1.7×10⁻⁵ - 1.9×10⁻⁵ |
| Reynolds number | Re | - | 10 - 10⁶ |
| Mach number | Ma | - | 0 - 0.3 |
| Drag coefficient | Cd | - | 0.1 - 24 |
| Lift coefficient | CL | - | 0 - 0.8 |
| Temperature | T | K | 250 - 320 |
| Pressure | p | Pa | 80000 - 101325 |
| Relative humidity | RH | % | 0 - 100 |
| Coefficient of restitution | e | - | 0 - 1 |
| Friction coefficient | μs, μk | - | 0 - 2 |
| Surface roughness | ε | m | 0 - 0.01 |

---

## List of Assumptions

1. **Spherical ball**: Perfect sphere with uniform density
2. **Rigid body**: No elastic deformation during flight
3. **Quiescent atmosphere**: No temperature inversions or layers
4. **Power law wind profile**: Valid for surface layer (z < 100m typically)
5. **Coulomb friction**: Constant friction coefficients during contact
6. **Instantaneous collision**: Contact duration << simulation timestep
7. **No thermal effects**: Ball temperature doesn't affect air properties locally
8. **Negligible electromagnetic forces**: No charged particles or magnetic fields
9. **Flat Earth**: No curvature or Coriolis effects
10. **Incompressible flow effects**: Density variations only with altitude, not velocity

---

*Document Version: 1.0*
*Last Updated: February 2026*