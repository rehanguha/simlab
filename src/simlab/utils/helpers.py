"""
Helper functions for formatting and utilities.

Contains utility functions for formatting output and common operations.
"""

def format_time(seconds: float) -> str:
    """
    Format time in a human-readable format.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    if seconds < 1:
        return f"{seconds*1000:.1f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds_remainder = seconds % 60
        return f"{minutes} min {seconds_remainder:.1f} s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_remainder = seconds % 60
        return f"{hours} h {minutes} min {seconds_remainder:.1f} s"

def format_distance(meters: float) -> str:
    """
    Format distance in a human-readable format.
    
    Args:
        meters (float): Distance in meters
        
    Returns:
        str: Formatted distance string
    """
    if meters < 0.001:
        return f"{meters*1000:.2f} mm"
    elif meters < 1:
        return f"{meters*100:.1f} cm"
    elif meters < 1000:
        return f"{meters:.2f} m"
    else:
        return f"{meters/1000:.2f} km"

def format_velocity(mps: float) -> str:
    """
    Format velocity in a human-readable format.
    
    Args:
        mps (float): Velocity in m/s
        
    Returns:
        str: Formatted velocity string
    """
    if mps < 1:
        return f"{mps*100:.1f} cm/s"
    elif mps < 10:
        return f"{mps:.2f} m/s"
    elif mps < 100:
        return f"{mps:.1f} m/s"
    else:
        return f"{mps/1000:.2f} km/s"

def format_mass(kg: float) -> str:
    """
    Format mass in a human-readable format.
    
    Args:
        kg (float): Mass in kg
        
    Returns:
        str: Formatted mass string
    """
    if kg < 0.001:
        return f"{kg*1000:.1f} g"
    elif kg < 1:
        return f"{kg*1000:.0f} g"
    elif kg < 1000:
        return f"{kg:.3f} kg"
    else:
        return f"{kg/1000:.3f} t"

def format_pressure(pascals: float) -> str:
    """
    Format pressure in a human-readable format.
    
    Args:
        pascals (float): Pressure in Pascals
        
    Returns:
        str: Formatted pressure string
    """
    if pascals < 1000:
        return f"{pascals:.0f} Pa"
    elif pascals < 100000:
        return f"{pascals/1000:.1f} kPa"
    else:
        return f"{pascals/100000:.2f} bar"

def format_temperature(kelvin: float) -> str:
    """
    Format temperature in a human-readable format.
    
    Args:
        kelvin (float): Temperature in Kelvin
        
    Returns:
        str: Formatted temperature string
    """
    celsius = kelvin - 273.15
    if -50 <= celsius <= 50:
        return f"{celsius:.1f} °C"
    else:
        return f"{kelvin:.1f} K"

def format_angle(radians: float) -> str:
    """
    Format angle in degrees.
    
    Args:
        radians (float): Angle in radians
        
    Returns:
        str: Formatted angle string
    """
    degrees = radians * 180 / 3.141592653589793
    return f"{degrees:.1f}°"

def format_percentage(value: float) -> str:
    """
    Format value as percentage.
    
    Args:
        value (float): Value between 0 and 1
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value*100:.1f}%"

def format_scientific(value: float, precision: int = 2) -> str:
    """
    Format value in scientific notation.
    
    Args:
        value (float): Value to format
        precision (int): Number of decimal places
        
    Returns:
        str: Formatted scientific notation string
    """
    return f"{value:.{precision}e}"

def format_number(value: float, precision: int = 3) -> str:
    """
    Format number with appropriate units and precision.
    
    Args:
        value (float): Number to format
        precision (int): Number of significant digits
        
    Returns:
        str: Formatted number string
    """
    if abs(value) >= 1e6:
        return f"{value/1e6:.{precision}f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.{precision}f}k"
    elif abs(value) >= 1:
        return f"{value:.{precision}f}"
    elif abs(value) >= 1e-3:
        return f"{value*1e3:.{precision}f}m"
    elif abs(value) >= 1e-6:
        return f"{value*1e6:.{precision}f}μ"
    else:
        return f"{value:.{precision}e}"