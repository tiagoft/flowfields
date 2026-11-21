"""Helpers for opening images and for working with 2D vectors."""

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


def kmeans(
    data: np.ndarray,
    n_clusters: int,
    rng: np.random.Generator | int | None = None,
    max_iter: int = 100,
    tol: float = 1e-4,
) -> tuple[np.ndarray, np.ndarray]:
    """Group points into n_clusters clusters with k-means

    The first centers are chosen with k-means++: each new center is a data
    point drawn with probability proportional to its squared distance to the
    nearest center so far.  Then each point goes to its nearest center and
    each center moves to the mean of its points (Lloyd's algorithm).  It
    stops when no point changes cluster, when the centers move less than
    ``tol`` times the variance of the data (the sum of the squared moves,
    over the mean variance of the dimensions, as in scikit-learn), or after
    max_iter rounds.  A cluster that loses all its points keeps its previous
    center.

    Args:
        data (np.ndarray): Points with shape (n_points, n_dims), such as the
            pixels of an image reshaped to (H * W, 3)
        n_clusters (int): Number of clusters, from 1 to n_points
        rng (np.random.Generator | int | None): Random generator for the
            first centers, or a seed for one.  None takes a fresh seed from
            the operating system.
        max_iter (int): Maximum number of rounds
        tol (float): Relative tolerance on the moves of the centers

    Returns:
        tuple[np.ndarray, np.ndarray]: The centers, with shape
            (n_clusters, n_dims), and the cluster of each point, with shape
            (n_points,)
    """
    rng = np.random.default_rng(rng)
    data = np.asarray(data, dtype=float)
    n_points = data.shape[0]
    if not 1 <= n_clusters <= n_points:
        raise ValueError(
            f"n_clusters must be between 1 and {n_points}, got {n_clusters}")

    # k-means++ initialization
    centers = np.empty((n_clusters, data.shape[1]))
    centers[0] = data[rng.integers(n_points)]
    distances = np.sum((data - centers[0])**2, axis=1)
    for k in range(1, n_clusters):
        total = np.sum(distances)
        if total > 0:
            idx = rng.choice(n_points, p=distances / total)
        else:  # every point is already on a center
            idx = rng.integers(n_points)
        centers[k] = data[idx]
        distances = np.minimum(distances, np.sum((data - centers[k])**2, axis=1))

    # Lloyd's algorithm
    threshold = tol * np.mean(np.var(data, axis=0))
    labels = _nearest_center(data, centers)
    for _ in range(max_iter):
        moved = 0.0
        for k in range(n_clusters):
            members = data[labels == k]
            if len(members) > 0:
                new_center = np.mean(members, axis=0)
                moved += np.sum((new_center - centers[k])**2)
                centers[k] = new_center
        new_labels = _nearest_center(data, centers)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        if moved <= threshold:
            break

    return centers, labels


def _nearest_center(data: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """Index of the nearest center to each point; ties go to the first one"""
    best = np.full(data.shape[0], np.inf)
    labels = np.zeros(data.shape[0], dtype=int)
    for k in range(centers.shape[0]):
        distances = np.sum((data - centers[k])**2, axis=1)
        closer = distances < best
        best[closer] = distances[closer]
        labels[closer] = k
    return labels


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
    """Round the angle of a 2D vector to one of n_levels directions

    The directions are evenly spaced, starting at angle 0.  The length of the
    vector does not change.

    Args:
        v (np.ndarray): Input vector
        n_levels (int): Number of allowed directions

    Returns:
        np.ndarray: Quantized vector
    """
    radius, angle = cartesian_to_polar(v)
    #quantized_radius = round(radius * n_levels) / n_levels
    quantized_angle = round(angle /
                            (2 * np.pi) * n_levels) * (2 * np.pi / n_levels)
    return polar_to_cartesian(radius, quantized_angle)
