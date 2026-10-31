import numpy as np
from PIL import Image


def open_image(filename: str, mode: str = "RGB") -> np.ndarray:
    """Open an image file as an array of pixels

    Args:
        filename (str): Path to the image file
        mode (str): Pillow color mode. Use "RGB" for color and "L" for
            grayscale.

    Returns:
        np.ndarray: Pixels as floats in [0, 1], with shape (H, W, 3) for "RGB"
            and (H, W) for "L"
    """
    with Image.open(filename) as img:
        return np.array(img.convert(mode), dtype=float) / 255.0


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


def clamp_vector(
    v: np.ndarray,
    min_length: float,
    max_length: float,
) -> np.ndarray:
    """Clamp a vector's length between a minimum and maximum value

    Args:
        v (np.ndarray): Input vector
        min_length (float): Minimum length
        max_length (float): Maximum length

    Returns:
        np.ndarray: Clamped vector
    """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    clamped_norm = clamp(norm, min_length, max_length)
    return v / norm * clamped_norm


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
                                [np.sin(angle), np.cos(angle)]])
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
    quantized_angle = round(angle /
                            (2 * np.pi) * n_levels) * (2 * np.pi / n_levels)
    return polar_to_cartesian(radius, quantized_angle)
