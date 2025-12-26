import numpy as np
import matplotlib.pyplot as plt
import tstudio.vector_fields
import tstudio.scalar_fields
import tstudio.utils
from tqdm import tqdm
import cairo

from itertools import product


def run():
    np.random.seed(42)
    
    field1 = tstudio.vector_fields.RotationField(
        center=np.array([0, 0]),
        direction=1,
        normalize=True,
    )
    field2 = tstudio.vector_fields.ExpansionField(
        center=np.array([0, 0]),
        direction=1,
        normalize=True,
    )
    vortex = tstudio.vector_fields.FieldSum(
        fields=[field1, field2],
        weights=[1.0, 0.25],
    )
    
    fieldExpansion = tstudio.vector_fields.ExpansionField(
        center=np.array([-6, -6]),
        direction=1,
        normalize=True,
    )
    fieldNoise = tstudio.vector_fields.NoiseField()
    fieldGaussian1 = tstudio.scalar_fields.GaussianField(
        center=np.array([-6, -6]),
        sigma=5.0,
        scale=1.5,
    )
    fieldGaussian2 = tstudio.scalar_fields.GaussianField(
        center=np.array([6, 6]),
        sigma=6.0,
        scale=1.0,
    )
    bgField = tstudio.vector_fields.FieldSum(
        fields=[fieldExpansion, fieldNoise],
        weights=[fieldGaussian1, fieldGaussian2],
    )
    
    focus = tstudio.scalar_fields.GaussianField(
        center=np.array([0, 0]),
        sigma=3.0,
        scale=2.0,
    )
    field = tstudio.vector_fields.FieldSum(
        fields=[vortex, bgField],
        weights=[focus, tstudio.scalar_fields.ConstantField(1.0)],
    )
    

    c1 = tstudio.scalar_fields.GaussianField(np.array([0.7, 1.1]), sigma=2)
    colorization = lambda x: 0.01 + 0.99 * np.tanh(c1(x))

    width_cm = 10
    height_cm = 10
    dpi = 300
    cm_to_inch = 1 / 2.54
    width_px = int(width_cm * cm_to_inch * dpi)
    height_px = int(height_cm * cm_to_inch * dpi)
    n_steps = 50
    step_size = 0.01
    rotation_angle = 0
    quantization_levels = None

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width_px, height_px)
    ctx = cairo.Context(surface)

    # White background
    # Off-white background: (0.961, 0.949, 0.922)
    ctx.set_source_rgb(0.961, 0.949, 0.922)
    ctx.paint()

    ctx.translate(width_px / 2, height_px / 2)

    scale = min(width_px, height_px) / 10.0
    ctx.scale(scale, -scale)
    ctx.set_line_width(0.02)

    for _ in tqdm(range(10000)):
        x = np.random.uniform(low=-5, high=5, size=2)

        # if np.random.rand() < prob_red(x):
        #     # Red: (0.796, 0.427, 0.318)
        #     ctx.set_source_rgba(0.796, 0.427, 0.318, colorization(x))
        # else:
        # Blue: (0.196, 0.322, 0.482)
        ctx.set_source_rgba(0.196, 0.322, 0.482, colorization(x))

        ctx.move_to(x[0], x[1])
        for _ in range(n_steps):
            dx = field(x) * step_size
            if rotation_angle != 0:
                dx = tstudio.utils.rotate_vector(dx, rotation_angle)
            if quantization_levels is not None:
                dx = tstudio.utils.quantize_vector(dx, quantization_levels)
            x_ = x + dx
            ctx.line_to(x_[0], x_[1])
            x = x_

        ctx.stroke()

    # fname = source code filename without extension
    fname = __file__.split('/')[-1].split('.')[0] + '.png'
    surface.write_to_png(fname)


if __name__ == "__main__":
    run()
