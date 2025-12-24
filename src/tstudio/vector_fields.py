import numpy as np 
from tstudio.scalar_fields import ScalarField

class FlowField():
    def __init__(self):
        pass
    
    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Returns the flowfield vector at point x.
        """
        raise NotImplementedError("Subclasses should implement this method.")
    
class RotationField(FlowField):
    def __init__(self, center: np.ndarray, sense: int = 1):
        super().__init__()
        self.center = center
        self.sense = sense

    def __call__(self, x: np.ndarray) -> np.ndarray:
        r = x - self.center
        y = np.array([-r[1], r[0]])
        y = y * self.sense
        y = y / np.linalg.norm(y)
        return y

class ExpansionField(FlowField):
    def __init__(self, center: np.ndarray, sense: int = 1):
        super().__init__()
        self.center = center
        self.sense = sense
        
    def __call__(self, x: np.ndarray) -> np.ndarray:
        r = x - self.center
        y = r / np.linalg.norm(r)
        y = y * self.sense
        return y
    
class FieldSum(FlowField):
    def __init__(self, fields: list[FlowField],
                 weights: None | list[float] | list[ScalarField] = None):
        self.list_of_fields = fields
        self.weights = weights

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
        y = y / np.linalg.norm(y) if np.linalg.norm(y) != 0 else y
        return y    