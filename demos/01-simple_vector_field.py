import numpy as np
import matplotlib.pyplot as plt
import tstudio.vector_fields
import tstudio.scalar_fields
import tstudio.utils
from tqdm import tqdm

def run():
    field1 = tstudio.vector_fields.RotationField(np.array([1, 1]))
    field2 = tstudio.vector_fields.ExpansionField(np.array([-1, -1]),
                                                  direction=1)

    w1 = tstudio.scalar_fields.GaussianField(
        np.array([1, 1]),
        sigma=3,
    )
    w2 = tstudio.scalar_fields.GaussianField(
        np.array([-1, -1]),
        sigma=1.5,
    )

    field = tstudio.vector_fields.FieldSum(
        fields=[field1, field2],
        weights=[w1, w2],
    )

    xlim = (-3, 3)
    ylim = (-3, 3)
    grid_size = (20, 20)

    x_vals = np.linspace(xlim[0], xlim[1], grid_size[0])
    y_vals = np.linspace(ylim[0], ylim[1], grid_size[1])
    X, Y = np.meshgrid(x_vals, y_vals)
    Zx = np.zeros_like(X)
    Zy = np.zeros_like(Y)

    for i in tqdm(range(grid_size[0])):
        for j in range(grid_size[1]):
            point = np.array([X[i, j], Y[i, j]])
            vector = field(point)
            Zx[i, j] = vector[0]
            Zy[i, j] = vector[1]
    plt.figure(figsize=(6, 6))
    plt.quiver(X, Y, Zx, Zy)
    plt.xlim(xlim)
    plt.ylim(ylim)
    #plt.title("Simple Vector Field")
    plt.savefig("01-simple_vector_field.png")
    plt.show()
    
if __name__ == "__main__":
    run()