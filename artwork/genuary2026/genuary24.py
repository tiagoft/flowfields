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
        np.array([2, -0.5]),
        direction=1,
    )
    field2 = tstudio.vector_fields.RotationField(
        np.array([-3, 0.5]),
        direction=-1,
    )

    w1 = tstudio.scalar_fields.GaussianField(
        np.array([1.9, -0.5]),
        sigma=1,
        scale=3.0,
    )
    w2 = tstudio.scalar_fields.GaussianField(
        np.array([-3, 0.5]),
        sigma=1,
        scale=1.0,
    )

    field = tstudio.vector_fields.FieldSum(
        fields=[field1, field2],
        weights=[w1, w2],
    )

    c1 = tstudio.scalar_fields.GaussianField(np.array([0.7, 1.1]), sigma=2)
    colorization = lambda x : 0.01 + 0.99 * np.tanh(c1(x))

    width_cm = 10
    height_cm = 10
    dpi = 300
    cm_to_inch = 1 / 2.54
    width_px = int(width_cm * cm_to_inch * dpi)
    height_px = int(height_cm * cm_to_inch * dpi)
    n_steps = 5000
    step_size = 0.01
    rotation_angle = 0
    quantization_levels = 7

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width_px, height_px)
    ctx = cairo.Context(surface)

    # White background
    # Off-white background: (0.961, 0.949, 0.922)
    ctx.set_source_rgb(0.961, 0.949, 0.922)
    ctx.paint()

    ctx.translate(width_px / 2, height_px / 2)

    scale = min(width_px, height_px) / 10.0
    ctx.scale(scale, -scale)
    ctx.set_line_width(0.05)

    print("Drawing...")
    for _ in tqdm(range(10)):
        x = np.random.uniform(low=-5.0, high=5.0, size=(2,))
        
        # if np.random.rand() < prob_red(x):
        #     # Red: (0.796, 0.427, 0.318)
        #     ctx.set_source_rgba(0.796, 0.427, 0.318, colorization(x))
        # else:
        # Blue: (0.196, 0.322, 0.482)
        

        ctx.move_to(x[0], x[1])

        ctx.set_source_rgba(0.196, 0.322, 0.482, 0.7)
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
