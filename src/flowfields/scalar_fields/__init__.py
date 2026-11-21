"""Scalar fields: functions that give a number for each point in the plane."""

from flowfields.scalar_fields.base import ScalarField
from flowfields.scalar_fields.gaussian import GaussianField
from flowfields.scalar_fields.constant import ConstantField
from flowfields.scalar_fields.box import BoxField
from flowfields.scalar_fields.matrix import MatrixField, KernelProbabilisticMatrixField

__all__ = [
    "ScalarField",
    "GaussianField",
    "ConstantField",
    "BoxField",
    "MatrixField",
    "KernelProbabilisticMatrixField",
]
