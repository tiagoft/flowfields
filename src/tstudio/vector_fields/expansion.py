import numpy as np

from tstudio.utils import normalize_vector
from tstudio.vector_fields.base import FlowField, _register_field


@_register_field
class ExpansionField(FlowField):
    """
    Radial expansion / contraction field centred at a fixed point.

    At each point x the vector points directly away from (or toward) the centre:

        v(x) = direction * (x - center)

    ``direction = +1`` produces an outward (source / expansion) field;
    ``direction = -1`` produces an inward (sink / contraction) field.

    If ``normalize=True`` (default) the output is divided by its L2 norm,
    giving a pure radial direction independent of distance from the centre.
    """

    def __init__(
        self,
        center: np.ndarray,
        direction: int = 1,
        normalize: bool = True,
        **kwargs,
    ):
        super().__init__()
        self.center = center
        self.direction = direction
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        y = x - self.center
        y = y * self.direction
        if self.normalize:
            y = normalize_vector(y)
        return y

    def to_dict(self) -> dict:
        return {
            "type": "ExpansionField",
            "center": self.center.tolist(),
            "direction": int(self.direction),
            "normalize": bool(self.normalize),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ExpansionField":
        return cls(
            center=np.array(d["center"]),
            direction=d.get("direction", 1),
            normalize=d.get("normalize", True),
        )
