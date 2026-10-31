"""Scalar fields: functions that give a number for each point in the plane."""

from tstudio.scalar_fields.base import ScalarField
from tstudio.scalar_fields.gaussian import GaussianField
from tstudio.scalar_fields.constant import ConstantField
from tstudio.scalar_fields.box import BoxField
from tstudio.scalar_fields.matrix import MatrixField, KernelProbabilisticMatrixField

__all__ = [
    "ScalarField",
    "GaussianField",
    "ConstantField",
    "BoxField",
    "MatrixField",
    "KernelProbabilisticMatrixField",
]
