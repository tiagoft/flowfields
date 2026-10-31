"""Vector field that returns random vectors."""

import numpy as np

from tstudio.utils import normalize_vector
from tstudio.vector_fields.base import FlowField


class NoiseField(FlowField):
    """
    Spatially-uncorrelated uniform random vector field.

    Each call samples a fresh vector independently of position:

        v ~ Uniform(-1, 1)^n

    where n is the dimensionality of the input x.  Because each evaluation is
    independent, this field is non-deterministic and has no spatial coherence.

    If ``normalize=True`` (default) the random vector is divided by its L2
    norm, producing a random unit direction.  Directions are not uniform:
    sampling from a square favours the diagonals.

    Args:
        normalize: Whether to L2-normalise the output vector.
        **kwargs: Ignored.
    """

    def __init__(
        self,
        normalize: bool = True,
        **kwargs,
    ):
        super().__init__()
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Returns a new random vector with the same shape as x.
        """
        noise = np.random.uniform(low=-1.0, high=1.0, size=x.shape)
        if self.normalize:
            noise = normalize_vector(noise)
        return noise
