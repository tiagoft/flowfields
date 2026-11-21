"""Scalar field with the shape of a Gaussian bump."""

import numpy as np

from flowfields.scalar_fields.base import ScalarField


class GaussianField(ScalarField):
    """
    Isotropic Gaussian (radial basis) scalar field.

    Returns a bell-shaped value centred at a fixed point:

        f(x) = scale * exp( -||x - center||^2 / (2 * sigma^2) )

    The peak value is ``scale`` at x = ``center`` and decays symmetrically in
    all directions with standard deviation ``sigma``.  Useful as a
    smooth, spatially-localised weight.

    Args:
        center: Peak location.
        sigma:  Spread of the Gaussian; larger values produce a wider bell.
        scale:  Peak amplitude (default 1.0).
    """

    def __init__(self,
                 center: np.ndarray,
                 sigma: float = 1.0,
                 scale: float = 1.0):
        self.center = center
        self.sigma = sigma
        self.scale = scale

    def __call__(self, x: np.ndarray) -> float:
        """
        Returns the scalar field value at point x.
        """
        return self.scale * np.exp(-np.sum(
            (x - self.center)**2) / (2 * self.sigma**2))
