import numpy as np


class ScalarField():
    """
    Abstract base class for scalar fields.

    Subclasses implement ``__call__`` to return a single float value f(x) at
    any point x in the plane.  Scalar fields are used as position-dependent
    weights in ``FieldSum``, ``FieldMax``, and ``FieldSelect``.
    """

    def __init__(self):
        pass

    def __call__(self, x: np.ndarray) -> float:
        """
        Returns the scalar field value at point x.
        """
        raise NotImplementedError("Subclasses should implement this method.")


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


class BoxField(ScalarField):
    """
    Axis-aligned rectangular indicator field.

    Returns one of two constant values depending on whether x lies inside the
    box defined by ``min_corner`` and ``max_corner``:

        f(x) = inside_value   if  min_corner <= x <= max_corner  (element-wise)
               outside_value  otherwise

    The corners are automatically sorted at construction time, so passing them
    in either order is safe.  Useful for hard spatial masking or gating.

    Args:
        min_corner:    Lower-left corner of the box.
        max_corner:    Upper-right corner of the box.
        inside_value:  Value returned for points strictly inside the box
                       (default 1.0).
        outside_value: Value returned for points outside the box (default 0.0).
    """

    def __init__(
        self,
        min_corner: np.ndarray,
        max_corner: np.ndarray,
        inside_value: float = 1.0,
        outside_value: float = 0.0,
    ):
        min_corner_ = np.minimum(min_corner, max_corner)
        max_corner_ = np.maximum(min_corner, max_corner)
        self.min_corner = min_corner_
        self.max_corner = max_corner_
        self.inside_value = inside_value
        self.outside_value = outside_value

    def __call__(self, x: np.ndarray) -> float:
        if np.all(x >= self.min_corner) and np.all(x <= self.max_corner):
            return self.inside_value
        else:
            return self.outside_value
