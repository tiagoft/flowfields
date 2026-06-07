import numpy as np

from tstudio.scalar_fields import ScalarField, scalar_from_dict

_FIELD_REGISTRY: dict[str, type] = {}


def _register_field(cls):
    _FIELD_REGISTRY[cls.__name__] = cls
    return cls


def field_from_dict(d: dict) -> "FlowField":
    """Reconstruct a FlowField from its dict representation."""
    return _FIELD_REGISTRY[d["type"]].from_dict(d)


def _serialize_weight(w) -> float | dict | None:
    if w is None:
        return None
    if isinstance(w, ScalarField):
        return w.to_dict()
    return float(w)


def _deserialize_weight(w) -> float | ScalarField | None:
    if w is None:
        return None
    if isinstance(w, dict):
        return scalar_from_dict(w)
    return float(w)


class FlowField():
    """
    Abstract base class for 2D vector fields.

    Subclasses implement ``__call__`` to return a flow vector v(x) at any
    point x in the plane.  The optional ``normalize`` flag (supported by most
    subclasses) divides the result by its L2 norm so that ||v(x)|| = 1.
    """

    def __init__(
        self,
        **kwargs,
    ):
        pass

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Returns the flowfield vector at point x.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def to_dict(self) -> dict:
        raise NotImplementedError("Subclasses should implement this method.")

    @classmethod
    def from_dict(cls, d: dict) -> "FlowField":
        raise NotImplementedError("Subclasses should implement this method.")
