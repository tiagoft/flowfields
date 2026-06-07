import numpy as np

from tstudio.scalar_fields import ScalarField
from tstudio.utils import normalize_vector
from tstudio.vector_fields.base import (
    FlowField,
    _deserialize_weight,
    _register_field,
    _serialize_weight,
    field_from_dict,
)


@_register_field
class FieldSum(FlowField):
    """
    Weighted linear combination of multiple flow fields.

    At each point x the output is the sum of all constituent field vectors,
    each scaled by its corresponding weight:

        v(x) = sum_i  w_i(x) * F_i(x)

    Weights ``w_i`` can be:
    - ``None``        — all fields contribute equally (weight 1).
    - ``float``       — a fixed scalar multiplier.
    - ``ScalarField`` — a position-dependent multiplier evaluated at x,
                        allowing spatially-varying blending.

    If ``normalize=True`` (default) the summed vector is divided by its L2
    norm so that ||v(x)|| = 1.
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

    def to_dict(self) -> dict:
        return {
            "type": "FieldSum",
            "normalize": bool(self.normalize),
            "fields": [f.to_dict() for f in self.list_of_fields],
            "weights": [_serialize_weight(w) for w in self.weights] if self.weights is not None else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FieldSum":
        weights_raw = d.get("weights")
        return cls(
            fields=[field_from_dict(f) for f in d["fields"]],
            weights=[_deserialize_weight(w) for w in weights_raw] if weights_raw is not None else None,
            normalize=d.get("normalize", True),
        )
