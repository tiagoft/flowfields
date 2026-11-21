"""Vector fields: functions that give a vector for each point in the plane."""

from flowfields.vector_fields.base import FlowField
from flowfields.vector_fields.rotation import RotationField
from flowfields.vector_fields.expansion import ExpansionField
from flowfields.vector_fields.noise import NoiseField
from flowfields.vector_fields.sum import FieldSum
from flowfields.vector_fields.max import FieldMax
from flowfields.vector_fields.select import FieldSelect

__all__ = [
    "FlowField",
    "RotationField",
    "ExpansionField",
    "NoiseField",
    "FieldSum",
    "FieldMax",
    "FieldSelect",
]
