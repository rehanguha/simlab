"""
Physical constants used throughout the simulation.

Contains standard physical constants and reference values.
"""

# Physical constants
GRAVITY = 9.80665  # m/s^2 - Standard gravitational acceleration
PI = 3.141592653589793  # π

# Standard atmospheric conditions at sea level
AIR_DENSITY = 1.225  # kg/m^3 - Standard air density at 15°C and sea level
AIR_VISCOSITY = 1.789e-5  # Pa·s - Dynamic viscosity of air at 15°C
SPEED_OF_SOUND = 340.3  # m/s - Speed of sound in air at 15°C

# Earth constants
EARTH_RADIUS = 6371000  # meters
EARTH_MASS = 5.972e24  # kg

# Material properties (typical values)
STEEL_DENSITY = 7850  # kg/m^3
ALUMINUM_DENSITY = 2700  # kg/m^3
RUBBER_DENSITY = 1100  # kg/m^3
PLASTIC_DENSITY = 900  # kg/m^3

# Common ball properties
TENNIS_BALL_MASS = 0.057  # kg
TENNIS_BALL_RADIUS = 0.033  # m
BASEBALL_MASS = 0.145  # kg
BASEBALL_RADIUS = 0.0366  # m
GOLF_BALL_MASS = 0.0459  # kg
GOLF_BALL_RADIUS = 0.02135  # m
BASKETBALL_MASS = 0.624  # kg
BASKETBALL_RADIUS = 0.119  # m

# Simulation constants
DEFAULT_TIME_STEP = 0.001  # seconds
DEFAULT_MAX_TIME = 30.0  # seconds
DEFAULT_TOLERANCE = 1e-6  # numerical tolerance

# Advanced physical constants for ISA model and aerodynamics
PHYSICAL_CONSTANTS = {
    # Gas constants
    'R': 287.058,           # J/(kg·K) - gas constant for dry air
    'R_v': 461.495,         # J/(kg·K) - gas constant for water vapor
    'gamma': 1.4,           # - ratio of specific heats for air
    
    # Standard conditions
    'T0': 288.15,           # K - standard temperature at sea level
    'p0': 101325,           # Pa - standard pressure at sea level
    'g': 9.80665,           # m/s² - standard gravity
    
    # Sutherland constants
    'mu_ref': 1.716e-5,     # Pa·s - reference viscosity
    'T_ref': 273.15,        # K - reference temperature
    'S': 110.4,             # K - Sutherland constant
    
    # Temperature lapse rate
    'L': 0.0065,            # K/m - temperature lapse rate
    
    # Material properties
    'E_default': 1e7,       # Pa - default Young's modulus
    'nu_default': 0.5,      # - default Poisson's ratio
}
