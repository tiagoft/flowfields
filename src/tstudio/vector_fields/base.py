import numpy as np

class FlowField():
    """
    Abstract base class for 2D vector fields.

    Subclasses implement ``__call__`` to return a flow vector v(x) at any
    point x in the plane.  The optional ``normalize`` flag (supported by most
    subclasses) divides the result by its L2 norm so that ||v(x)|| = 1.
    """

    def __init__(
        self,
        **kwargs,
    ):
        pass

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Returns the flowfield vector at point x.
        """
        raise NotImplementedError("Subclasses should implement this method.")
