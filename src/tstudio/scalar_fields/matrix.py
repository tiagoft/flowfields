import numpy as np

from tstudio.scalar_fields.base import ScalarField, _register_scalar


@_register_scalar
class MatrixField(ScalarField):
    """
    Matrix-based scalar field.

    This field is defined by a 2D array of scalar values, and a spatial
    bounding box that maps the array indices to a region in space. The field
    value at any point is obtained by bilinear interpolation of the
    array values.
    """

    def __init__(
        self,
        min_corner: np.ndarray,
        max_corner: np.ndarray,
        data: np.ndarray,
        normalize: bool = False,
    ):
        min_corner_ = np.minimum(min_corner, max_corner)
        max_corner_ = np.maximum(min_corner, max_corner)
        self.min_corner = min_corner_
        self.max_corner = max_corner_
        self.data = data
        self.normalize = normalize
        if self.normalize:
            self.data = self.data - np.min(self.data)
            if np.max(self.data) > 0:
                self.data = self.data / np.max(self.data)

    def __call__(self, x: np.ndarray) -> float:
        if np.all(x >= self.min_corner) and np.all(x <= self.max_corner):
            # Perform bilinear interpolation
            t = (x - self.min_corner) / (self.max_corner - self.min_corner)
            t = np.clip(t, 0.0, 1.0)

            # self.data is indexed [row, col]: row grows downward (cartesian y,
            # flipped) and col grows rightward (cartesian x).
            rc = np.array([1.0 - t[1], t[0]]) * (np.array(self.data.shape) - 1)
            i0 = np.floor(rc).astype(int)
            i1 = np.ceil(rc).astype(int)
            w = rc - i0
            v00 = self.data[i0[0], i0[1]]
            v01 = self.data[i0[0], i1[1]]
            v10 = self.data[i1[0], i0[1]]
            v11 = self.data[i1[0], i1[1]]
            zval = (
                (1 - w[0]) * (1 - w[1]) * v00
                + (1 - w[0]) * w[1] * v01
                + w[0] * (1 - w[1]) * v10
                + w[0] * w[1] * v11
            )
            return zval
        else:
            return 0.0

    def to_dict(self) -> dict:
        return {
            "type": "MatrixField",
            "min_corner": self.min_corner.tolist(),
            "max_corner": self.max_corner.tolist(),
            "data": self.data.tolist(),
            "normalize": self.normalize,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MatrixField":
        return cls(
            min_corner=np.array(d["min_corner"]),
            max_corner=np.array(d["max_corner"]),
            data=np.array(d["data"]),
            normalize=d.get("normalize", False),
        )

    def plot_figure(
        self,
        output_filename,
        figsize=(4, 4),
        dpi=100,
        cmap="gray",
        vmin=0,
        vmax=1,
    ):
        import matplotlib.pyplot as plt

        plt.figure(figsize=figsize)
        plt.imshow(self.data, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.colorbar()
        # plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_filename, dpi=dpi)
        plt.close()


@_register_scalar
class KernelProbabilisticMatrixField(MatrixField):
    """
    A matrix field that applies a Gaussian kernel to the input coordinates
    before performing bilinear interpolation. This allows for a smoother
    transition between values in the matrix.
    """

    def __init__(
        self,
        min_corner: np.ndarray,
        max_corner: np.ndarray,
        data: np.ndarray,
        normalize: bool = False,
        sigma: float = 1.0, # The standard deviation of the Gaussian kernel
                            # The scale here is relative to the size of the bounding box, so a value of 1.0 means that the kernel
                            # will have a standard deviation equal to the 
                            # size of the bounding box.
    ):
        super().__init__(
            min_corner,
            max_corner,
            data,
            normalize,
        )
        self.sigma = sigma

    def __call__(self, x: np.ndarray) -> float:
        if np.all(x >= self.min_corner) and np.all(x <= self.max_corner):
            # Apply Gaussian kernel
            center = (self.min_corner + self.max_corner) / 2
            distance = np.linalg.norm(x - center)
            weight = np.exp(-0.5 * (distance / self.sigma) ** 2)

            # Perform bilinear interpolation
            t = (x - self.min_corner) / (self.max_corner - self.min_corner)
            t = np.clip(t, 0.0, 1.0)

            rc = np.array([1.0 - t[1], t[0]]) * (np.array(self.data.shape) - 1)
            i0 = np.floor(rc).astype(int)
            i1 = np.ceil(rc).astype(int)
            w = rc - i0
            v00 = self.data[i0[0], i0[1]]
            v01 = self.data[i0[0], i1[1]]
            v10 = self.data[i1[0], i0[1]]
            v11 = self.data[i1[0], i1[1]]
            zval = (
                (1 - w[0]) * (1 - w[1]) * v00
                + (1 - w[0]) * w[1] * v01
                + w[0] * (1 - w[1]) * v10
                + w[0] * w[1] * v11
            )
            return weight * zval
        else:
            return 0.0
