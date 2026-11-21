"""Vector field that returns random vectors."""

import numpy as np

from flowfields.utils import normalize_vector
from flowfields.vector_fields.base import FlowField


class NoiseField(FlowField):
    """
    Spatially-uncorrelated random vector field.

    Each call samples a fresh vector independently of position:

        v ~ Normal(0, 1)^n     if ``distribution="gaussian"`` (default)
        v ~ Uniform(-1, 1)^n   if ``distribution="uniform"``

    where n is the dimensionality of the input x.  Because each evaluation is
    independent, this field is non-deterministic and has no spatial coherence.

    If ``normalize=True`` (default) the random vector is divided by its L2
    norm, producing a random unit direction.  All directions are equally likely
    with ``"gaussian"``, while ``"uniform"`` samples from a square, which
    favours the diagonals.

    Args:
        normalize: Whether to L2-normalise the output vector.
        distribution: Distribution of each coordinate, either ``"gaussian"`` or
            ``"uniform"``.
        rng: Random generator, or a seed for one.  ``None`` takes a fresh
            seed from the operating system.
        **kwargs: Ignored.
    """

    def __init__(
        self,
        normalize: bool = True,
        distribution: str = "gaussian",
        rng: np.random.Generator | int | None = None,
        **kwargs,
    ):
        super().__init__()
        if distribution not in ("gaussian", "uniform"):
            raise ValueError(f"Unknown distribution: {distribution}")
        self.normalize = normalize
        self.distribution = distribution
        self.rng = np.random.default_rng(rng)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Returns a new random vector with the same shape as x.
        """
        if self.distribution == "gaussian":
            noise = self.rng.normal(size=x.shape)
        else:
            noise = self.rng.uniform(low=-1.0, high=1.0, size=x.shape)
        if self.normalize:
            noise = normalize_vector(noise)
        return noise
