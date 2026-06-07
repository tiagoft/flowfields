import numpy as np

_SCALAR_REGISTRY: dict[str, type] = {}


def _register_scalar(cls):
    _SCALAR_REGISTRY[cls.__name__] = cls
    return cls


def scalar_from_dict(d: dict) -> "ScalarField":
    """Reconstruct a ScalarField from its dict representation."""
    return _SCALAR_REGISTRY[d["type"]].from_dict(d)


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

    def to_dict(self) -> dict:
        raise NotImplementedError("Subclasses should implement this method.")

    @classmethod
    def from_dict(cls, d: dict) -> "ScalarField":
        raise NotImplementedError("Subclasses should implement this method.")
