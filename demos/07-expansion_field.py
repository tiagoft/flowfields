import numpy as np
import tstudio.vector_fields as vf
from _common import arrows, panels, save, strokes

center = np.zeros(2)
fields = {
    "direction=1": vf.ExpansionField(center, direction=1),
    "direction=-1": vf.ExpansionField(center, direction=-1),
    "normalize=False": vf.ExpansionField(center, normalize=False),
}

fig, axes = panels(list(fields))
for ax, field in zip(axes, fields.values()):
    strokes(ax, field)
    arrows(ax, field)
save(fig, __file__)
