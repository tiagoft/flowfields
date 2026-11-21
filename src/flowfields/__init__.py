"""Generative-art toolkit built around composable vector, scalar and color fields.

Every field is available from the package itself::

    import flowfields as ff

    field = ff.FieldSum(
        fields=[ff.RotationField(center), ff.NoiseField(rng=0)],
        weights=[ff.GaussianField(center, sigma=2.0), 0.2],
    )

The submodules ``vector_fields``, ``scalar_fields``, ``color_fields`` and
``utils`` remain available as well.
"""

from importlib.metadata import PackageNotFoundError, version

from flowfields import color_fields, scalar_fields, utils, vector_fields
from flowfields.color_fields import ColorField, MatrixColorField
from flowfields.scalar_fields import (
    BoxField,
    ConstantField,
    GaussianField,
    KernelProbabilisticMatrixField,
    MatrixField,
    ScalarField,
)
from flowfields.vector_fields import (
    ExpansionField,
    FieldMax,
    FieldSelect,
    FieldSum,
    FlowField,
    NoiseField,
    RotationField,
)

try:
    __version__ = version("flowfields")
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "unknown"

__all__ = [
    "__version__",
    # submodules
    "color_fields",
    "scalar_fields",
    "utils",
    "vector_fields",
    # scalar fields
    "ScalarField",
    "GaussianField",
    "ConstantField",
    "BoxField",
    "MatrixField",
    "KernelProbabilisticMatrixField",
    # vector fields
    "FlowField",
    "RotationField",
    "ExpansionField",
    "NoiseField",
    "FieldSum",
    "FieldMax",
    "FieldSelect",
    # color fields
    "ColorField",
    "MatrixColorField",
]
