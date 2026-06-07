import numpy as np

from tstudio.utils import normalize_vector
from tstudio.vector_fields.base import FlowField, _register_field


@_register_field
class RotationField(FlowField):
    """
    Curl / rotation field centred at a fixed point.

    At each point x the vector is the radius vector rotated 90° in the plane:

        r = x - center
        v(x) = direction * [-r_y, r_x]

    This produces circular streamlines around ``center``.
    ``direction = +1`` gives counter-clockwise rotation;
    ``direction = -1`` gives clockwise rotation.

    If ``normalize=True`` (default) the output is divided by its L2 norm,
    giving unit-speed circular flow regardless of distance from the centre.
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
        r = x - self.center
        y = np.array([-r[1], r[0]], dtype=float)
        y = y * self.direction
        if self.normalize:
            y = normalize_vector(y)
        return y

    def to_dict(self) -> dict:
        return {
            "type": "RotationField",
            "center": self.center.tolist(),
            "direction": int(self.direction),
            "normalize": bool(self.normalize),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RotationField":
        return cls(
            center=np.array(d["center"]),
            direction=d.get("direction", 1),
            normalize=d.get("normalize", True),
        )
