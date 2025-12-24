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
    def __init__(self, center: np.ndarray, sigma: float = 1.0, scale : float = 1.0):
        self.center = center
        self.sigma = sigma
        self.scale = scale

    def __call__(self, x: np.ndarray) -> float:
        return self.scale * np.exp(-np.sum((x - self.center) ** 2) / (2 * self.sigma ** 2))
    

class ConstantField(ScalarField):
    def __init__(self, value: float = 1.0):
        self.value = value

    def __call__(self, x: np.ndarray) -> float:
        return self.value