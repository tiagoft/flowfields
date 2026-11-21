import numpy as np
import matplotlib.pyplot as plt
import flowfields.vector_fields
import flowfields.scalar_fields
import flowfields.utils
from tqdm import tqdm
import cairo

from itertools import product

number_per_level = [3, 5, 8, 13]

def _in_range(center, radius, point):
    return np.linalg.norm(point - center) <= radius

def _in_range_list(centers, radius, point):
    return [_in_range(center, radius, point) for center in centers]

def run():
    
    level = 1
    radius = 0
    radius_delta = 0.75
    
    fields = []
    weights = []
    
    for i in range(len(number_per_level)):
        radius += radius_delta
        for j in range(number_per_level[i]):
            if (i+j)%2 == 0:
                continue
            
            angle = j * (2 * np.pi / number_per_level[i])
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
    
    fields.append(flowfields.vector_fields.ExpansionField(np.array([0,0]), direction=-1))
    weights.append(flowfields.scalar_fields.ConstantField(0.1))

    field = flowfields.vector_fields.FieldSum(
        fields=fields,
        weights=weights,
    )

    c1 = flowfields.scalar_fields.GaussianField(np.array([0.7, 1.1]), sigma=2)
    colorization = lambda x : 0.01 + 0.99 * np.tanh(c1(x))

    width_cm = 10
    height_cm = 10
    dpi = 300
    cm_to_inch = 1 / 2.54
    width_px = int(width_cm * cm_to_inch * dpi)
    height_px = int(height_cm * cm_to_inch * dpi)
    n_steps = 50
    step_size = 0.01
    rotation_angle = 0
    quantization_levels = 3
    quantization_radius = 2.0
    centers = [
        np.array([0,0]),
        np.array([2,2]),
        np.array([-2,2]),
        np.array([2,-2]),
        np.array([-2,-2]),
    ]

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
                dx = flowfields.utils.rotate_vector(dx, rotation_angle)
            if quantization_levels is not None:
                locus = _in_range_list(centers, quantization_radius, x)
                if locus[0] and not (locus[1] or locus[2] or locus[3] or locus[4]):
                    dx = flowfields.utils.quantize_vector(dx, quantization_levels)
                elif locus[1] or locus[0] and not (locus[2] or locus[3] or locus[4]):
                    dx = flowfields.utils.quantize_vector(dx, quantization_levels+1)
                elif locus[2] or locus[3]:
                    dx = flowfields.utils.quantize_vector(dx, quantization_levels+2)
                elif locus[4]:
                    dx = flowfields.utils.quantize_vector(dx, quantization_levels+3)
                
    
            x_ = x + dx
            ctx.line_to(x_[0], x_[1])
            x = x_

        ctx.stroke()

    # fname = source code filename without extension
    fname = __file__.split('/')[-1].split('.')[0] + '.png'
    surface.write_to_png(fname)


if __name__ == "__main__":
    run()
