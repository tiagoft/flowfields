import numpy as np
import yaml

def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Normalize a vector in cartesian form

    Args:
        v (np.ndarray): Input vector

    Returns:
        np.ndarray: Normalized vector
    """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def lerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    """Linear interpolation between two vectors

    Args:
        a (np.ndarray): First vector
        b (np.ndarray): Second vector
        t (float): Interpolation factor (0 <= t <= 1)

    Returns:
        np.ndarray: Interpolated vector
    """
    return (1 - t) * a + t * b

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between a minimum and maximum value

    Args:
        value (float): Input value
        min_value (float): Minimum value
        max_value (float): Maximum value

    Returns:
        float: Clamped value
    """
    return max(min_value, min(value, max_value))

def cartesian_to_polar(v: np.ndarray) -> tuple[float, float]:
    """Convert a 2D vector from cartesian to polar coordinates

    Args:
        v (np.ndarray): Input vector in cartesian coordinates
    Returns:
        tuple[float, float]: (radius, angle) in polar coordinates
    """
    radius = np.linalg.norm(v)
    angle = np.arctan2(v[1], v[0])
    return radius, angle

def polar_to_cartesian(radius: float, angle: float) -> np.ndarray:
    """Convert polar coordinates to a 2D cartesian vector

    Args:
        radius (float): Radius in polar coordinates
        angle (float): Angle in polar coordinates

    Returns:
        np.ndarray: Vector in cartesian coordinates
    """
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return np.array([x, y])

def rotate_vector(v: np.ndarray, angle: float) -> np.ndarray:
    """Rotate a 2D vector by a given angle

    Args:
        v (np.ndarray): Input vector
        angle (float): Rotation angle in radians

    Returns:
        np.ndarray: Rotated vector
    """
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                [np.sin(angle),  np.cos(angle)]])
    return rotation_matrix @ v

def quantize_vector(v: np.ndarray, n_levels: int) -> np.ndarray:
    """Quantize a vector to a given number of levels

    Args:
        v (np.ndarray): Input vector
        n_levels (int): Number of quantization levels

    Returns:
        np.ndarray: Quantized vector
    """
    radius, angle = cartesian_to_polar(v)
    #quantized_radius = round(radius * n_levels) / n_levels
    quantized_angle = round(angle / (2 * np.pi) * n_levels) * (2 * np.pi / n_levels)
    return polar_to_cartesian(radius, quantized_angle)


def save_field_yaml(field, path: str) -> None:
    """Serialize a FlowField tree to a YAML file."""
    with open(path, "w") as f:
        yaml.dump(field.to_dict(), f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def load_field_yaml(path: str):
    """Load a FlowField tree from a YAML file."""
    from tstudio.vector_fields import field_from_dict
    with open(path) as f:
        return field_from_dict(yaml.safe_load(f))


def save_scalar_yaml(field, path: str) -> None:
    """Serialize a ScalarField to a YAML file."""
    with open(path, "w") as f:
        yaml.dump(field.to_dict(), f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def load_scalar_yaml(path: str):
    """Load a ScalarField from a YAML file."""
    from tstudio.scalar_fields import scalar_from_dict
    with open(path) as f:
        return scalar_from_dict(yaml.safe_load(f))