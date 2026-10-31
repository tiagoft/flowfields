import numpy as np

from tstudio.scalar_fields import ScalarField
from tstudio.utils import normalize_vector
from tstudio.vector_fields.base import FlowField


class FieldMax(FlowField):
    """
    Hard-selection field that returns the vector of the highest-weighted field.

    At each point x the weights are evaluated and the winning field is chosen:

        i* = argmax_i  w_i(x)
        v(x) = F_{i*}(x)

    Weights can be fixed scalars or ``ScalarField`` instances evaluated at x,
    so the dominant field can change continuously across space.  This produces
    sharp, discontinuous transitions at boundaries where two weights are equal.
    With ``weights=None`` all weights are equal, so the first field always wins.

    If ``normalize=True`` (default) the selected vector is divided by its L2
    norm.
    """

    def __init__(
        self,
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
            else:
                magnitudes.append(1.0)

        idx = np.argmax(magnitudes)
        y = self.list_of_fields[idx](x)

        if self.normalize:
            y = normalize_vector(y)

        return y
