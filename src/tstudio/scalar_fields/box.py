"""Scalar field with one value inside a rectangle and another outside of it."""

import numpy as np

from tstudio.scalar_fields.base import ScalarField


class BoxField(ScalarField):
    """
    Axis-aligned rectangular indicator field.

    Returns one of two constant values depending on whether x lies inside the
    box defined by ``min_corner`` and ``max_corner``:

        f(x) = inside_value   if  min_corner <= x <= max_corner  (element-wise)
               outside_value  otherwise

    The corners are automatically sorted at construction time, so passing them
    in either order is safe.  Useful for hard spatial masking or gating.

    Args:
        min_corner:    Lower-left corner of the box.
        max_corner:    Upper-right corner of the box.
        inside_value:  Value returned for points inside the box, borders
                       included (default 1.0).
        outside_value: Value returned for points outside the box (default 0.0).
    """

    def __init__(
        self,
        min_corner: np.ndarray,
        max_corner: np.ndarray,
        inside_value: float = 1.0,
        outside_value: float = 0.0,
    ):
        min_corner_ = np.minimum(min_corner, max_corner)
        max_corner_ = np.maximum(min_corner, max_corner)
        self.min_corner = min_corner_
        self.max_corner = max_corner_
        self.inside_value = inside_value
        self.outside_value = outside_value

    def __call__(self, x: np.ndarray) -> float:
        """
        Returns the scalar field value at point x.
        """
        if np.all(x >= self.min_corner) and np.all(x <= self.max_corner):
            return self.inside_value
        else:
            return self.outside_value
