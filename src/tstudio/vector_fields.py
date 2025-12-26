import numpy as np
from tstudio.scalar_fields import ScalarField
from tstudio.utils import normalize_vector


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
            y = normalize_vector(y)
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
            y = normalize_vector(y)
        return y
    
class NoiseField(FlowField):
    def __init__(self, normalize: bool = True):
        super().__init__()
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        noise = np.random.uniform(low=-1.0, high=1.0, size=x.shape)
        if self.normalize:
            noise = normalize_vector(noise)
        return noise

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
            y = normalize_vector(y)
    
        return y


class FieldMax(FlowField):

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
        magnitudes = []
        
        for idx, field in enumerate(self.list_of_fields):

            if self.weights is not None:
                if isinstance(self.weights[idx], ScalarField):
                    weight_value = self.weights[idx](x)
                else:
                    weight_value = self.weights[idx]
                magnitudes.append(weight_value)
        
        idx = np.argmax(magnitudes)
        y = self.list_of_fields[idx](x)

        if self.normalize:
            y = normalize_vector(y)
    
        return y