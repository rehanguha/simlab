"""
Input validation for ball drop simulation.
Phase 2: Robustness - Physical bounds checking.
"""

from typing import List
from models import Params, Surface, Wind


class ValidationError(ValueError):
    """Custom exception for input validation errors."""
    pass


def validate_inputs(params: Params, surface: Surface, wind: Wind) -> List[str]:
    """
    Validate all simulation inputs for physical correctness.
    
    Returns a list of error messages. Empty list means all inputs are valid.
    """
    errors = []
    
    # Ball properties
    if params.mass <= 0:
        errors.append(f"mass must be > 0 kg, got {params.mass}")
    if params.radius <= 0:
        errors.append(f"radius must be > 0 m, got {params.radius}")
    if params.v0 < 0:
        errors.append(f"initial velocity v0 must be >= 0 m/s, got {params.v0}")
    if params.spin_rps < 0:
        errors.append(f"spin_rps must be >= 0, got {params.spin_rps}")
    
    # Spin axis validation
    spin_mag = (
        params.spin_axis[0]**2 + 
        params.spin_axis[1]**2 + 
        params.spin_axis[2]**2
    ) ** 0.5
    if params.spin_rps > 0 and spin_mag < 1e-10:
        errors.append("spin_axis must be non-zero when spin_rps > 0")
    
    # Position validation
    if params.z0 <= surface.base_height + params.radius:
        errors.append(
            f"z0 ({params.z0}) must be > ground height + radius "
            f"({surface.base_height + params.radius})"
        )
    
    # Time parameters
    if params.dt <= 0:
        errors.append(f"dt must be > 0, got {params.dt}")
    if params.t_max <= 0:
        errors.append(f"t_max must be > 0, got {params.t_max}")
    
    # Surface properties
    if not 0 <= surface.elasticity_base <= 1:
        errors.append(
            f"elasticity_base must be in [0, 1], got {surface.elasticity_base}"
        )
    if not 0 <= surface.friction_mu_s <= 2:
        errors.append(
            f"friction_mu_s must be in [0, 2], got {surface.friction_mu_s}"
        )
    if not 0 <= surface.friction_mu_k <= 2:
        errors.append(
            f"friction_mu_k must be in [0, 2], got {surface.friction_mu_k}"
        )
    
    # Wind properties
    if not 0 <= wind.humidity_pct <= 100:
        errors.append(
            f"humidity_pct must be in [0, 100], got {wind.humidity_pct}"
        )
    
    return errors


def validate_inputs_or_raise(params: Params, surface: Surface, wind: Wind) -> None:
    """
    Validate inputs and raise ValidationError if invalid.
    
    Raises:
        ValidationError: If any input validation fails.
    """
    errors = validate_inputs(params, surface, wind)
    if errors:
        error_msg = "Input validation failed:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        raise ValidationError(error_msg)


def validate_dataframe(df) -> List[str]:
    """
    Validate simulation output DataFrame.
    
    Checks for:
    - Required columns
    - Non-negative values where applicable
    - No NaN/Inf values
    """
    errors = []
    
    required_columns = [
        "Time", "X", "Y", "Z", "Vx", "Vy", "Vz", 
        "Ox", "Oy", "Oz", "AirDensity", "Mu", "Re", 
        "Cd", "WindX", "WindY", "WindZ", "Z_ground", 
        "Mach", "Dt_actual"
    ]
    
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
    
    # Check for NaN/Inf
    import numpy as np
    for col in df.columns:
        if df[col].dtype in [np.float64, np.float32]:
            nan_count = df[col].isna().sum()
            inf_count = np.isinf(df[col]).sum()
            if nan_count > 0:
                errors.append(f"Column '{col}' contains {nan_count} NaN values")
            if inf_count > 0:
                errors.append(f"Column '{col}' contains {inf_count} Inf values")
    
    return errors