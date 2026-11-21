"""Vector field that switches randomly between its fields as it is called."""

import numpy as np

from flowfields.scalar_fields import ScalarField
from flowfields.utils import normalize_vector, warn_unused_arguments
from flowfields.vector_fields.base import FlowField
from flowfields.vector_fields.sum import FieldSum


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
    The first set is sampled on the first call, with the weights at that
    point.

    **Interpolation**: when ``lerp_len > 0`` a transition between the outgoing
    and incoming active field is linearly interpolated over ``lerp_len`` calls:

        v(x) = (1 - t) * v_current(x) + t * v_next(x),   t = step / lerp_len

    After ``lerp_len`` steps the new field becomes the current field.

    If ``normalize=True`` (default) the final vector is divided by its L2 norm.

    Args:
        fields: List of candidate ``FlowField`` instances.
        weights: Per-field scalar or ``ScalarField`` weights used as selection
            probabilities.  ``None`` makes all fields equally likely.
        select_n: Number of fields to blend at each active selection.  Fewer
            are used if fewer fields have a non-zero weight at that point.
        change_id_prob: Probability of resampling the active field on each call.
        temperature: Controls distribution flatness; 0 = proportional to weight,
            higher values = more uniform.
        normalize: Whether to L2-normalise the output vector.  The active
            fields are always normalised, so ``False`` only keeps the length
            of vectors interpolated during a transition.
        lerp_len: Number of steps over which to interpolate between field
            transitions.  0 = instantaneous switch.
        rng: Random generator, or a seed for one.  ``None`` takes a fresh
            seed from the operating system.
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
        rng: np.random.Generator | int | None = None,
        **kwargs,
    ):
        warn_unused_arguments(self, kwargs)
        self.list_of_fields = fields
        self.weights = weights
        self.change_id_prob = change_id_prob
        self.normalize = normalize
        self.select_n = select_n
        self.temperature = temperature
        self.lerp_len = lerp_len
        self.lerp_count = 0
        self.rng = np.random.default_rng(rng)

        # The first fields are drawn on the first call, where the weights can
        # be evaluated
        self.last_idx = None
        self.current_field = None
        self.next_field = None

    def select_index(self, x: np.ndarray | None = None) -> np.ndarray:
        """
        Draws the indices of the fields to activate.

        Args:
            x: Point where the weights are evaluated.  If None, or if the field
                has no weights, all fields are equally likely.  The same happens
                if every weight is zero at x.

        Returns:
            Array with the drawn indices, without repetition.
        """
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

        magnitudes = np.array(magnitudes, dtype=float)
        total = np.sum(magnitudes)
        # If every weight is zero here, fall back to a uniform choice
        p = magnitudes / total if total > 0 else np.full(len(magnitudes), 1.0 / len(magnitudes))
        # Apply temperature to p, where higher temperature makes distribution more uniform
        if self.temperature > 0:
            p = p**(1.0 / (1.0 + self.temperature))
            p = p / np.sum(p)

        idx = self.rng.choice(
            len(self.list_of_fields),
            p=p,
            # Fields with zero probability are never drawn, even if that means
            # blending fewer than select_n fields
            size=min(self.select_n, np.count_nonzero(p)),
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
                or self.rng.random() < self.change_id_prob)\
                and self.lerp_count == 0:
            self.last_idx = self.select_index(x).tolist()
            fields = [self.list_of_fields[i] for i in self.last_idx]
            weights = [self.weights[i] for i in self.last_idx] if self.weights is not None else None
            self.next_field = FieldSum(
                fields=fields,
                weights=weights,
            )
            self.lerp_count = 0
            if self.current_field is None:  # first call: no transition
                self.current_field = self.next_field

        if self.current_field is self.next_field:
            y = self.current_field(x)
        elif self.lerp_count < self.lerp_len:
            t = self.lerp_count / self.lerp_len
            y = (1 - t) * self.current_field(x) + t * self.next_field(x)
            self.lerp_count += 1
        else:
            # The transition is over: the new field is used from this call on
            self.current_field = self.next_field
            self.lerp_count = 0
            y = self.current_field(x)

        if self.normalize:
            y = normalize_vector(y)

        return y
