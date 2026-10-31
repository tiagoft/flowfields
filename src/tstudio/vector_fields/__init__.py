"""Vector fields: functions that give a vector for each point in the plane."""

from tstudio.vector_fields.base import FlowField
from tstudio.vector_fields.rotation import RotationField
from tstudio.vector_fields.expansion import ExpansionField
from tstudio.vector_fields.noise import NoiseField
from tstudio.vector_fields.sum import FieldSum
from tstudio.vector_fields.max import FieldMax
from tstudio.vector_fields.select import FieldSelect

__all__ = [
    "FlowField",
    "RotationField",
    "ExpansionField",
    "NoiseField",
    "FieldSum",
    "FieldMax",
    "FieldSelect",
]
