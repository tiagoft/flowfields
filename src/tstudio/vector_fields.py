import numpy as np
from tstudio.scalar_fields import ScalarField
from tstudio.utils import normalize_vector


class FlowField():

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


class RotationField(FlowField):

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


class ExpansionField(FlowField):

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


class NoiseField(FlowField):

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


class FieldSum(FlowField):

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
                #print(weight_value, y_, y_.dtype)
                y_ *= weight_value

            y += y_
        if self.normalize:
            y = normalize_vector(y)

        return y


class FieldMax(FlowField):

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


class FieldSelect(FlowField):

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

        #print("Using fields:", self.last_idx)
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
