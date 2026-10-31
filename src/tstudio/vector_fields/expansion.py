"""Vector field that points away from or toward a center."""

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
    Otherwise the vector length equals the distance from the centre.

    Args:
        center: Point the flow moves away from or toward.
        direction: +1 for outward, -1 for inward.
        normalize: Whether to L2-normalise the output vector.
        **kwargs: Ignored.
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
        """
        Returns the flowfield vector at point x.
        """
        y = x - self.center
        y = y * self.direction
        if self.normalize:
            y = normalize_vector(y)
        return y
