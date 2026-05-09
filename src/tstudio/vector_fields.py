import numpy as np
from tstudio.scalar_fields import ScalarField, scalar_from_dict
from tstudio.utils import normalize_vector

_FIELD_REGISTRY: dict[str, type] = {}


def _register_field(cls):
    _FIELD_REGISTRY[cls.__name__] = cls
    return cls


def field_from_dict(d: dict) -> "FlowField":
    """Reconstruct a FlowField from its dict representation."""
    return _FIELD_REGISTRY[d["type"]].from_dict(d)


def _serialize_weight(w) -> float | dict | None:
    if w is None:
        return None
    if isinstance(w, ScalarField):
        return w.to_dict()
    return float(w)


def _deserialize_weight(w) -> float | ScalarField | None:
    if w is None:
        return None
    if isinstance(w, dict):
        return scalar_from_dict(w)
    return float(w)


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

    def to_dict(self) -> dict:
        raise NotImplementedError("Subclasses should implement this method.")

    @classmethod
    def from_dict(cls, d: dict) -> "FlowField":
        raise NotImplementedError("Subclasses should implement this method.")


@_register_field
class RotationField(FlowField):
    """
    Curl / rotation field centred at a fixed point.

    At each point x the vector is the radius vector rotated 90° in the plane:

        r = x - center
        v(x) = direction * [-r_y, r_x]

    This produces circular streamlines around ``center``.
    ``direction = +1`` gives counter-clockwise rotation;
    ``direction = -1`` gives clockwise rotation.

    If ``normalize=True`` (default) the output is divided by its L2 norm,
    giving unit-speed circular flow regardless of distance from the centre.
    """

    def __init__(
        self,
        center: np.ndarray,
        direction: int = 1,
        normalize: bool = True,
        **kwargs,
    ):
        super().__init__()
        self.center = center
        self.direction = direction
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        r = x - self.center
        y = np.array([-r[1], r[0]], dtype=float)
        y = y * self.direction
        if self.normalize:
            y = normalize_vector(y)
        return y

    def to_dict(self) -> dict:
        return {
            "type": "RotationField",
            "center": self.center.tolist(),
            "direction": int(self.direction),
            "normalize": bool(self.normalize),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RotationField":
        return cls(
            center=np.array(d["center"]),
            direction=d.get("direction", 1),
            normalize=d.get("normalize", True),
        )


@_register_field
class ExpansionField(FlowField):
    """
    Radial expansion / contraction field centred at a fixed point.

    At each point x the vector points directly away from (or toward) the centre:

        v(x) = direction * (x - center)

    ``direction = +1`` produces an outward (source / expansion) field;
    ``direction = -1`` produces an inward (sink / contraction) field.

    If ``normalize=True`` (default) the output is divided by its L2 norm,
    giving a pure radial direction independent of distance from the centre.
    """

    def __init__(
        self,
        center: np.ndarray,
        direction: int = 1,
        normalize: bool = True,
        **kwargs,
    ):
        super().__init__()
        self.center = center
        self.direction = direction
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        y = x - self.center
        y = y * self.direction
        if self.normalize:
            y = normalize_vector(y)
        return y

    def to_dict(self) -> dict:
        return {
            "type": "ExpansionField",
            "center": self.center.tolist(),
            "direction": int(self.direction),
            "normalize": bool(self.normalize),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ExpansionField":
        return cls(
            center=np.array(d["center"]),
            direction=d.get("direction", 1),
            normalize=d.get("normalize", True),
        )


@_register_field
class NoiseField(FlowField):
    """
    Spatially-uncorrelated uniform random vector field.

    Each call samples a fresh vector independently of position:

        v ~ Uniform(-1, 1)^n

    where n is the dimensionality of the input x.  Because each evaluation is
    independent, this field is non-deterministic and has no spatial coherence.

    If ``normalize=True`` (default) the random vector is divided by its L2
    norm, producing a uniformly-distributed random unit direction.
    """

    def __init__(
        self,
        normalize: bool = True,
        **kwargs,
    ):
        super().__init__()
        self.normalize = normalize

    def __call__(self, x: np.ndarray) -> np.ndarray:
        noise = np.random.uniform(low=-1.0, high=1.0, size=x.shape)
        if self.normalize:
            noise = normalize_vector(noise)
        return noise

    def to_dict(self) -> dict:
        return {
            "type": "NoiseField",
            "normalize": bool(self.normalize),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "NoiseField":
        return cls(normalize=d.get("normalize", True))


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


@_register_field
class FieldMax(FlowField):
    """
    Hard-selection field that returns the vector of the highest-weighted field.

    At each point x the weights are evaluated and the winning field is chosen:

        i* = argmax_i  w_i(x)
        v(x) = F_{i*}(x)

    Weights can be fixed scalars or ``ScalarField`` instances evaluated at x,
    so the dominant field can change continuously across space.  This produces
    sharp, discontinuous transitions at boundaries where two weights are equal.

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

        idx = np.argmax(magnitudes)
        y = self.list_of_fields[idx](x)

        if self.normalize:
            y = normalize_vector(y)

        return y

    def to_dict(self) -> dict:
        return {
            "type": "FieldMax",
            "normalize": bool(self.normalize),
            "fields": [f.to_dict() for f in self.list_of_fields],
            "weights": [_serialize_weight(w) for w in self.weights] if self.weights is not None else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FieldMax":
        weights_raw = d.get("weights")
        return cls(
            fields=[field_from_dict(f) for f in d["fields"]],
            weights=[_deserialize_weight(w) for w in weights_raw] if weights_raw is not None else None,
            normalize=d.get("normalize", True),
        )


@_register_field
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
            probabilities.  Must be provided (not None) for probabilistic use.
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
        weights = [self.weights[i] for i in self.last_idx]
        self.current_field = FieldSum(
            fields=fields,
            weights=weights,
        )
        self.next_field = self.current_field

    def select_index(self, x: np.ndarray | None = None) -> list[int]:
        magnitudes = []

        for idx, _ in enumerate(self.list_of_fields):

            if self.weights is not None:
                if x is not None:
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
            weights = [self.weights[i] for i in self.last_idx]
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

    def to_dict(self) -> dict:
        return {
            "type": "FieldSelect",
            "normalize": bool(self.normalize),
            "select_n": int(self.select_n),
            "change_id_prob": float(self.change_id_prob),
            "temperature": float(self.temperature),
            "lerp_len": int(self.lerp_len),
            "fields": [f.to_dict() for f in self.list_of_fields],
            "weights": [_serialize_weight(w) for w in self.weights] if self.weights is not None else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FieldSelect":
        weights_raw = d.get("weights")
        return cls(
            fields=[field_from_dict(f) for f in d["fields"]],
            weights=[_deserialize_weight(w) for w in weights_raw] if weights_raw is not None else None,
            select_n=d.get("select_n", 1),
            change_id_prob=d.get("change_id_prob", 0.1),
            temperature=d.get("temperature", 0.0),
            normalize=d.get("normalize", True),
            lerp_len=d.get("lerp_len", 0),
        )
