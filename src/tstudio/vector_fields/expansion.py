import numpy as np

from tstudio.utils import normalize_vector
from tstudio.vector_fields.base import FlowField


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
