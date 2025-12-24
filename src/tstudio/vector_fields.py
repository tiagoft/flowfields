import numpy as np
from tstudio.scalar_fields import ScalarField

def _normalize_vector(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

class FlowField():
    def __init__(self):
        pass

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Returns the flowfield vector at point x.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class RotationField(FlowField):

    def __init__(
        self,
        center: np.ndarray,
        direction: int = 1,
        normalize: bool = True,
    ):
        super().__init__()
        self.center = center
        self.direction = direction
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        r = x - self.center
        y = np.array([-r[1], r[0]])
        y = y * self.direction
        if self.normalize:
            y = _normalize_vector(y)
        return y


class ExpansionField(FlowField):
    def __init__(self, center: np.ndarray, direction: int = 1, normalize: bool = True):
        super().__init__()
        self.center = center
        self.direction = direction
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        y = x - self.center
        y = y * self.direction
        if self.normalize:
            y = _normalize_vector(y)
        return y

class FieldSum(FlowField):

    def __init__(self,
                 fields: list[FlowField],
                 weights: None | list[float] | list[ScalarField] = None,
                 normalize: bool = True,
                 ):
        self.list_of_fields = fields
        self.weights = weights
        self.normalize = normalize

    def __call__(
        self,
        x: np.ndarray,
    ) -> np.ndarray:
        """
        Returns the flowfield vector at point x.
        """
        y = np.zeros_like(x)
        for idx, field in enumerate(self.list_of_fields):
            y_ = field(x)
            if self.weights is not None:
                if isinstance(self.weights[idx], ScalarField):
                    weight_value = self.weights[idx](x)
                else:
                    weight_value = self.weights[idx]
                y_ *= weight_value

            y += y_
        if self.normalize:
            y = _normalize_vector(y)
    
        return y
