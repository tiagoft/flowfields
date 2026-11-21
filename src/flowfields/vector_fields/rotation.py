"""Vector field that circles around a center."""

import numpy as np

from flowfields.utils import normalize_vector, warn_unused_arguments
from flowfields.vector_fields.base import FlowField


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
    Otherwise the vector length equals the distance from the centre.

    Args:
        center: Point the flow rotates around.
        direction: +1 for counter-clockwise, -1 for clockwise.
        normalize: Whether to L2-normalise the output vector.
        **kwargs: Not used; each one gives an ``UnusedArgumentWarning``.
    """

    def __init__(
        self,
        center: np.ndarray,
        direction: int = 1,
        normalize: bool = True,
        **kwargs,
    ):
        warn_unused_arguments(self, kwargs)
        self.center = center
        self.direction = direction
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Returns the flowfield vector at point x.
        """
        r = x - self.center
        y = np.array([-r[1], r[0]], dtype=float)
        y = y * self.direction
        if self.normalize:
            y = normalize_vector(y)
        return y
