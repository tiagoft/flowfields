import numpy as np
import matplotlib.pyplot as plt
import flowfields.vector_fields
import flowfields.scalar_fields
import flowfields.utils
from tqdm import tqdm
import cairo

from itertools import product


def run():
    np.random.seed(42)
    
    fibonacci_sequence = [3, 5, 8, 13]
    radius_delta = 0.9
    radius = 0
    
    fields = []
    weights = []
    for i in range(len(fibonacci_sequence)):
        radius += radius_delta
        for j in range(fibonacci_sequence[i]):
            
            angle = j * (2 * np.pi / fibonacci_sequence[i]) + i * (0.25*np.pi / fibonacci_sequence[i])
            position = radius * np.array([np.cos(angle), np.sin(angle)])
            
            field = flowfields.vector_fields.RotationField(
                position,
                direction=1
            )
            
            weight = flowfields.scalar_fields.GaussianField(
                position,
                sigma=0.5,
                scale=1.0
            )
            
            fields.append(field)
            weights.append(weight)
    
    fields.append(flowfields.vector_fields.ExpansionField(np.array([0,0]), direction=1))
    weights.append(flowfields.scalar_fields.GaussianField(np.array([0,0]), sigma=0.1, scale=0.3))
    
    fields.append(flowfields.vector_fields.ExpansionField(np.array([0,0]), direction=-1))
    weights.append(flowfields.scalar_fields.GaussianField(np.array([0,0]), sigma=30, scale=0.1))
    
    field = flowfields.vector_fields.FieldSelect(
        fields=fields,
        weights=weights,
        change_id_prob=0.01,
        select_n=3,
        temperature=1.5,
        lerp_len = 30,
    )

    c1 = flowfields.scalar_fields.GaussianField(np.array([0.7, 1.1]), sigma=2)
    colorization = lambda x: 0.01 + 0.99 * np.tanh(c1(x))

    width_cm = 10
    height_cm = 10
    dpi = 300
    cm_to_inch = 1 / 2.54
    width_px = int(width_cm * cm_to_inch * dpi)
    height_px = int(height_cm * cm_to_inch * dpi)
    n_steps = 50000
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
    ctx.set_line_width(0.01)

    print("Drawing...")
    for _ in range(1):
        x = np.array([0, 0])
        
        # if np.random.rand() < prob_red(x):
        #     # Red: (0.796, 0.427, 0.318)
        #     ctx.set_source_rgba(0.796, 0.427, 0.318, colorization(x))
        # else:
        # Blue: (0.196, 0.322, 0.482)
        

        ctx.move_to(x[0], x[1])

        ctx.set_source_rgba(0.196, 0.322, 0.482, 1.0)
        for _ in tqdm(range(n_steps)):
            dx = field(x) * step_size
            if rotation_angle != 0:
                dx = flowfields.utils.rotate_vector(dx, rotation_angle)
            if quantization_levels is not None:
                dx = flowfields.utils.quantize_vector(dx, quantization_levels)
            x_ = x + dx
            ctx.line_to(x_[0], x_[1])
            x = x_

        ctx.stroke()

    # fname = source code filename without extension
    fname = __file__.split('/')[-1].split('.')[0] + '.png'
    surface.write_to_png(fname)


if __name__ == "__main__":
    run()
