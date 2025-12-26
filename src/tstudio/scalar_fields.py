import numpy as np


class ScalarField():

    def __init__(self):
        pass

    def __call__(self, x: np.ndarray) -> float:
        """
        Returns the scalar field value at point x.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class GaussianField(ScalarField):

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

    def __init__(self, value: float = 1.0):
        self.value = value

    def __call__(self, x: np.ndarray) -> float:
        return self.value


class BoxField(ScalarField):

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
