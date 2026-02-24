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