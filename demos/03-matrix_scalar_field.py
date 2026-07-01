import numpy as np
import matplotlib.pyplot as plt
import tstudio.vector_fields
import tstudio.scalar_fields
import tstudio.utils
from tqdm import tqdm
from PIL import Image
from scipy.ndimage import gaussian_filter
from pathlib import Path


def run():
    # Carrega e converte para escala de cinza
    curr_path = Path(__file__).parent
    img = Image.open(curr_path / "sunset.jpg").convert("L")
    matrix_data = np.array(img, dtype=float) / 255.0

    field1 = tstudio.vector_fields.RotationField(
        np.array([1, 1]),
        normalize=False,
    )
    field2 = tstudio.vector_fields.ExpansionField(np.array([-1, -1]),
                                                  direction=1)

    w1 = tstudio.scalar_fields.MatrixField(
        min_corner=np.array([-3, -3]),
        max_corner=np.array([3, 3]),
        data=gaussian_filter(matrix_data, sigma=20),
        normalize=True,
    )
    w1.plot_figure("03a-matrix_scalar_field_visualization.png")

    print(w1(np.array([1, 1])))
    print(w1(np.array([-1, -1])))

    w2 = tstudio.scalar_fields.ConstantField(value=0.4)

    field = tstudio.vector_fields.FieldSum(
        fields=[field1, field2],
        weights=[w1, w2],
        normalize=False,
    )

    xlim = (-3, 3)
    ylim = (-3, 3)

    n_lines = 50000
    scale = 1
    X = []
    Y = []
    Zx = []
    Zy = []

    for i in tqdm(range(n_lines)):
        # Select random position within xlim and ylim
        x = np.random.uniform(xlim[0], xlim[1])
        y = np.random.uniform(ylim[0], ylim[1])

        # Calculate vector field value at this position
        pos = np.array([x, y])
        vector = field(pos)
        vector = scale * vector
        vector = tstudio.utils.clamp_vector(vector, max_length=0.3, min_length=0.1)

        X.append([x, x + vector[0]])
        Y.append([y, y + vector[1]])

    X = np.array(X)
    Y = np.array(Y)
    plt.figure(figsize=(6, 6))
    plt.plot(X.T, Y.T, color='#0f4521', alpha=0.1)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xticks([])
    plt.yticks([])
    #plt.title("Simple Vector Field")
    plt.savefig("03-matrix_scalar_field.png")
    plt.show()


if __name__ == "__main__":
    run()
