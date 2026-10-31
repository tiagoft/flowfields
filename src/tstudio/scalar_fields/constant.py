"""Scalar field with the same value everywhere."""

import numpy as np

from tstudio.scalar_fields.base import ScalarField


class ConstantField(ScalarField):
    """
    Uniform scalar field that returns the same value everywhere.

        f(x) = value

    Useful as a fixed-weight placeholder wherever a ``ScalarField`` is expected
    but spatial variation is not needed.

    Args:
        value: The constant scalar value returned at every point (default 1.0).
    """

    def __init__(self, value: float = 1.0):
        self.value = value

    def __call__(self, x: np.ndarray) -> float:
        """
        Returns the scalar field value at point x.
        """
        return self.value
