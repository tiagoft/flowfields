import numpy as np
import tstudio.vector_fields as vf
from _common import panels, save, strokes

noise = vf.NoiseField()
noisy_rotation = vf.FieldSum(
    fields=[vf.RotationField(np.zeros(2)), noise],
    weights=[1.0, 1.0],
)

fig, axes = panels(["normalize=True", "normalize=False", "added to a rotation"])
strokes(axes[0], noise, n_lines=60, n_steps=500, start=np.zeros(2), step=0.02)
strokes(axes[1], vf.NoiseField(normalize=False), n_lines=60, n_steps=500, start=np.zeros(2), step=0.02)
strokes(axes[2], noisy_rotation)
save(fig, __file__)
