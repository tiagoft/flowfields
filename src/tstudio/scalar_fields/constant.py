import numpy as np

from tstudio.scalar_fields.base import ScalarField, _register_scalar


@_register_scalar
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
        return self.value

    def to_dict(self) -> dict:
        return {
            "type": "ConstantField",
            "value": float(self.value),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ConstantField":
        return cls(value=d.get("value", 1.0))
