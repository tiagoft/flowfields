import numpy as np

from tstudio.scalar_fields import ScalarField
from tstudio.utils import normalize_vector
from tstudio.vector_fields.base import FlowField
from tstudio.vector_fields.sum import FieldSum


class FieldSelect(FlowField):
    """
    Stateful probabilistic field selector with optional smooth transitions.

    At each call this field may stochastically switch to a new active sub-field
    (or blend of sub-fields).  The selection is governed by a softmax-like
    distribution over the weights:

        p_i(x) ∝ w_i(x)^(1 / (1 + T))

    where T = ``temperature``.  T = 0 keeps the raw weight ratios; larger T
    flattens the distribution toward uniform, making all fields equally likely.

    ``select_n`` fields are drawn without replacement from this distribution and
    combined via ``FieldSum`` to form the active field.

    **Switching**: with probability ``change_id_prob`` at each call a new set of
    ``select_n`` fields is sampled (using weights evaluated at the current x).

    **Interpolation**: when ``lerp_len > 0`` a transition between the outgoing
    and incoming active field is linearly interpolated over ``lerp_len`` calls:

        v(x) = (1 - t) * v_current(x) + t * v_next(x),   t = step / lerp_len

    After ``lerp_len`` steps the new field becomes the current field.

    If ``normalize=True`` (default) the final vector is divided by its L2 norm.

    Args:
        fields: List of candidate ``FlowField`` instances.
        weights: Per-field scalar or ``ScalarField`` weights used as selection
            probabilities.  ``None`` makes all fields equally likely.
        select_n: Number of fields to blend at each active selection.
        change_id_prob: Probability of resampling the active field on each call.
        temperature: Controls distribution flatness; 0 = proportional to weight,
            higher values = more uniform.
        normalize: Whether to L2-normalise the output vector.
        lerp_len: Number of steps over which to interpolate between field
            transitions.  0 = instantaneous switch.
    """

    def __init__(
        self,
        fields: list[FlowField],
        weights: None | list[float] | list[ScalarField] = None,
        select_n: int = 1,
        change_id_prob: float = 0.1,
        temperature: float = 0.0,
        normalize: bool = True,
        lerp_len: int = 0,
    ):
        self.list_of_fields = fields
        self.weights = weights
        self.change_id_prob = change_id_prob
        self.normalize = normalize
        self.select_n = select_n
        self.temperature = temperature
        self.lerp_len = lerp_len
        self.lerp_count = 0

        self.last_idx = self.select_index().tolist()
        fields = [self.list_of_fields[i] for i in self.last_idx]
        weights = [self.weights[i] for i in self.last_idx] if self.weights is not None else None
        self.current_field = FieldSum(
            fields=fields,
            weights=weights,
        )
        self.next_field = self.current_field

    def select_index(self, x: np.ndarray | None = None) -> list[int]:
        magnitudes = []

        for idx, _ in enumerate(self.list_of_fields):

            if self.weights is not None and x is not None:
                if isinstance(self.weights[idx], ScalarField):
                    weight_value = self.weights[idx](x)
                else:
                    weight_value = self.weights[idx]

                magnitudes.append(weight_value)
            else:
                magnitudes.append(1.0)

        p = np.array(magnitudes) / np.sum(magnitudes)
        # Apply temperature to p, where higher temperature makes distribution more uniform
        if self.temperature > 0:
            p = p**(1.0 / (1.0 + self.temperature))
            p = p / np.sum(p)

        idx = np.random.choice(
            len(self.list_of_fields),
            p=p,
            size=self.select_n,
            replace=False,
        )
        return idx

    def __call__(
        self,
        x: np.ndarray,
    ) -> np.ndarray:
        """
        Returns the flowfield vector at point x.
        """
        if (self.last_idx is None\
                or np.random.rand() < self.change_id_prob)\
                and self.lerp_count == 0:
            self.last_idx = self.select_index(x).tolist()
            fields = [self.list_of_fields[i] for i in self.last_idx]
            weights = [self.weights[i] for i in self.last_idx] if self.weights is not None else None
            self.next_field = FieldSum(
                fields=fields,
                weights=weights,
            )
            self.lerp_count = 0

        y_curr = self.current_field(x)
        if self.current_field != self.next_field:
            if self.lerp_count < self.lerp_len:
                t = self.lerp_count / self.lerp_len
                y_next = self.next_field(x)
                y = (1 - t) * y_curr + t * y_next
                self.lerp_count += 1
            else:
                self.current_field = self.next_field
                self.lerp_count = 0
                y = y_curr
        else:
            y = y_curr

        if self.normalize:
            y = normalize_vector(y)

        return y
