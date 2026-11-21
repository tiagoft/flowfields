"""Vector field that uses only the highest-weighted of its fields at each point."""

import numpy as np

from flowfields.scalar_fields import ScalarField
from flowfields.utils import normalize_vector, warn_unused_arguments
from flowfields.vector_fields.base import FlowField


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

    Args:
        fields: The candidate ``FlowField`` instances.
        weights: One weight per field.  ``None`` gives all fields the same
            weight.
        normalize: Whether to L2-normalise the output vector.
    """

    def __init__(
        self,
        fields: list[FlowField],
        weights: None | list[float] | list[ScalarField] = None,
        normalize: bool = True,
        **kwargs,
    ):
        warn_unused_arguments(self, kwargs)
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
