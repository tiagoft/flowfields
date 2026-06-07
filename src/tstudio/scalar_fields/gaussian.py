import numpy as np

from tstudio.scalar_fields.base import ScalarField, _register_scalar


@_register_scalar
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
        return self.scale * np.exp(-np.sum(
            (x - self.center)**2) / (2 * self.sigma**2))

    def to_dict(self) -> dict:
        return {
            "type": "GaussianField",
            "center": self.center.tolist(),
            "sigma": float(self.sigma),
            "scale": float(self.scale),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GaussianField":
        return cls(
            center=np.array(d["center"]),
            sigma=d.get("sigma", 1.0),
            scale=d.get("scale", 1.0),
        )
