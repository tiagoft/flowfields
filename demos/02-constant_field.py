import numpy as np
import flowfields.scalar_fields as sf
import flowfields.vector_fields as vf
from _common import panels, save, strokes

# A constant weight sets how much of each field goes into a blend everywhere:
# here, how open the spiral of a rotation plus an expansion is.
rotation = vf.RotationField(np.zeros(2))
expansion = vf.ExpansionField(np.zeros(2))
values = [0.0, 0.3, 2.0]

fig, axes = panels([f"expansion weight={value}" for value in values])
for ax, value in zip(axes, values):
    field = vf.FieldSum(
        fields=[rotation, expansion],
        weights=[sf.ConstantField(1.0), sf.ConstantField(value)],
    )
    strokes(ax, field)
save(fig, __file__)
