import numpy as np
import matplotlib.pyplot as plt
import tstudio.vector_fields
import tstudio.scalar_fields
import tstudio.utils
from tqdm import tqdm
import cairo

from itertools import product


def run():
    fields = []
    boxes = []
    np.random.seed(42)
    for i in range(20):
        center = np.random.normal(loc=0, scale=3, size=2)
        size = np.random.uniform(low=0.5, high=4.0, size=2)
        value = np.random.uniform(low=0.5, high=2.5)
        box_min = center - size / 2
        box_max = center + size / 2

        field = tstudio.vector_fields.RotationField(
            center,
            direction=np.random.choice([-1, 1]),
        )
        box = tstudio.scalar_fields.BoxField(
            box_min,
            box_max,
            inside_value=value,
            outside_value=0.0,
        )
        fields.append(field)
        boxes.append(box)



    field0 = tstudio.vector_fields.ExpansionField(
        np.array([-5,-5]),
        direction=1,
    )
    fieldnoise = tstudio.vector_fields.NoiseField(normalize=True)
    wnoise = tstudio.scalar_fields.GaussianField(
        np.array([5,5]),
        sigma=5.0,
        scale=0.1,
    )
    w0 = tstudio.scalar_fields.ConstantField(0.05)
    bf_field = tstudio.vector_fields.FieldSum(
        fields=[field0, fieldnoise],
        weights=[w0, wnoise],
    )
    
    
    
    
    fields.append(bf_field)
    weights = boxes + [w0]
    field = tstudio.vector_fields.FieldMax(
        fields=fields,
        weights=weights,
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
