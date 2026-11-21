"""Color fields: functions that give a color for each point in the plane."""

from flowfields.color_fields.base import ColorField
from flowfields.color_fields.matrixcolorfield import MatrixColorField

__all__ = [
    "ColorField",
    "MatrixColorField",
]
