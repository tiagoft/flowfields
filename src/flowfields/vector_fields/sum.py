"""Vector field that adds its fields with weights."""

import numpy as np

from flowfields.scalar_fields import ScalarField
from flowfields.utils import normalize_vector
from flowfields.vector_fields.base import FlowField


class FieldSum(FlowField):
    """
    Weighted linear combination of multiple flow fields.

    At each point x the output is the sum of all constituent field vectors,
    each scaled by its corresponding weight:

        v(x) = sum_i  w_i(x) * F_i(x)

    Each weight ``w_i`` can be:
    - ``float``       — a fixed scalar multiplier.
    - ``ScalarField`` — a position-dependent multiplier evaluated at x,
                        allowing spatially-varying blending.

    If ``normalize=True`` (default) the summed vector is divided by its L2
    norm so that ||v(x)|| = 1.

    Args:
        fields: The ``FlowField`` instances to add.
        weights: One weight per field.  ``None`` gives all fields weight 1.
        normalize: Whether to L2-normalise the output vector.
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
        y = np.zeros_like(x, dtype=float)
        for idx, field in enumerate(self.list_of_fields):
            y_ = field(x) * 1.0
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
