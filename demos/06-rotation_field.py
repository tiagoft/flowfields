import numpy as np
import flowfields.vector_fields as vf
from _common import arrows, panels, save, strokes

center = np.zeros(2)
fields = {
    "direction=1": vf.RotationField(center, direction=1),
    "direction=-1": vf.RotationField(center, direction=-1),
    "normalize=False": vf.RotationField(center, normalize=False),
}

fig, axes = panels(list(fields))
for ax, field in zip(axes, fields.values()):
    strokes(ax, field)
    arrows(ax, field)
save(fig, __file__)
