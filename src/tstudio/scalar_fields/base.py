import numpy as np

class ScalarField():
    """
    Abstract base class for scalar fields.

    Subclasses implement ``__call__`` to return a single float value f(x) at
    any point x in the plane.  Scalar fields are used as position-dependent
    weights in ``FieldSum``, ``FieldMax``, and ``FieldSelect``.
    """

    def __init__(self):
        pass

    def __call__(self, x: np.ndarray) -> float:
        """
        Returns the scalar field value at point x.
        """
        raise NotImplementedError("Subclasses should implement this method.")
