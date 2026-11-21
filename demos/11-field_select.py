import numpy as np
import tstudio.scalar_fields as sf
import tstudio.vector_fields as vf
from _common import RNG, panels, save, strokes

# FieldSelect keeps switching between fields as it is called, so a single long
# line wanders through all of them.
angles = np.linspace(0, 2 * np.pi, 6, endpoint=False)
centers = [0.5 * np.array([np.cos(a), np.sin(a)]) for a in angles]
fields = [vf.RotationField(center) for center in centers]
weights = [sf.GaussianField(center, sigma=0.5) for center in centers]

options = {
    "lerp_len=0": dict(lerp_len=0),
    "lerp_len=50": dict(lerp_len=50),
    "select_n=3, temperature=2": dict(select_n=3, temperature=2.0, lerp_len=50),
}

fig, axes = panels(list(options))
for ax, kwargs in zip(axes, options.values()):
    field = vf.FieldSelect(fields, weights, change_id_prob=0.01, rng=RNG, **kwargs)
    strokes(ax, field, n_lines=1, n_steps=8000, start=np.zeros(2), alpha=0.9)
save(fig, __file__)
