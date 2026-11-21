"""Abstract base class for color fields."""

import numpy as np
from flowfields.utils import warn_unused_arguments

class ColorField():
    """
    Abstract base class for color fields.

    Subclasses implement ``__call__`` to return a color at any point x in the
    plane.
    """

    def __init__(
        self,
        **kwargs,
    ):
        warn_unused_arguments(self, kwargs)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Returns the RGB color at point x.
        """
        raise NotImplementedError("ColorField is an abstract class and cannot be called directly.")
    
