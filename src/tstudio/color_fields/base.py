import numpy as np

class ColorField():
    def __init__(
        self,
    ):
        pass

    def __call__(self, x: np.ndarray) -> float:
        raise NotImplementedError("ColorField is an abstract class and cannot be called directly.")
    
