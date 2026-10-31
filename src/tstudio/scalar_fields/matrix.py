"""Scalar fields that read their values from a 2D array, such as an image."""

import numpy as np

from tstudio.scalar_fields.base import ScalarField


class MatrixField(ScalarField):
    """
    Matrix-based scalar field.

    This field is defined by a 2D array of scalar values, and a spatial
    bounding box that maps the array indices to a region in space. The field
    value at any point is obtained by bilinear interpolation of the
    array values.  The first row of the array is at the top of the box (the
    highest y), as in an image, and the field is 0 outside the box.

    Args:
        min_corner: One corner of the bounding box.
        max_corner: The opposite corner of the bounding box.
        data: 2D array of values.
        normalize: Whether to rescale ``data`` to the range [0, 1].
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
        """
        Returns the scalar field value at point x.
        """
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

    def plot_figure(
        self,
        output_filename,
        figsize=(4, 4),
        dpi=100,
        cmap="gray",
        vmin=0,
        vmax=1,
    ):
        """
        Saves an image of the matrix with a colorbar.

        Args:
            output_filename: Path of the file to write.
            figsize: Figure size in inches.
            dpi: Figure resolution.
            cmap: Matplotlib colormap name.
            vmin: Value at the bottom of the colormap.
            vmax: Value at the top of the colormap.
        """
        import matplotlib.pyplot as plt

        plt.figure(figsize=figsize)
        plt.imshow(self.data, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.colorbar()
        # plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_filename, dpi=dpi)
        plt.close()


class KernelProbabilisticMatrixField(MatrixField):
    """
    A ``MatrixField`` multiplied by a Gaussian centred on its bounding box:

        f(x) = exp( -||x - c||^2 / (2 * sigma^2) ) * m(x)

    where c is the centre of the box and m(x) is the ``MatrixField`` value, so
    the values fade toward the borders of the box.

    Args:
        min_corner: One corner of the bounding box.
        max_corner: The opposite corner of the bounding box.
        data: 2D array of values.
        normalize: Whether to rescale ``data`` to the range [0, 1].
        sigma: Spread of the Gaussian, in the same units as x.
    """

    def __init__(
        self,
        min_corner: np.ndarray,
        max_corner: np.ndarray,
        data: np.ndarray,
        normalize: bool = False,
        sigma: float = 1.0,
    ):
        super().__init__(
            min_corner,
            max_corner,
            data,
            normalize,
        )
        self.sigma = sigma

    def __call__(self, x: np.ndarray) -> float:
        """
        Returns the scalar field value at point x.
        """
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
