"""Abstract base class for scalar fields."""

import numpy as np
from flowfields.utils import warn_unused_arguments

class ScalarField():
    """
    Abstract base class for scalar fields.

    Subclasses implement ``__call__`` to return a single float value f(x) at
    any point x in the plane.  Scalar fields are used as position-dependent
    weights in ``FieldSum``, ``FieldMax``, and ``FieldSelect``.
    """

    def __init__(self, **kwargs):
        warn_unused_arguments(self, kwargs)

    def __call__(self, x: np.ndarray) -> float:
        """
        Returns the scalar field value at point x.
        """
        raise NotImplementedError("Subclasses should implement this method.")
