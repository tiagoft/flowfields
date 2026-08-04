import numpy as np
import matplotlib.pyplot as plt
import tstudio.vector_fields
import tstudio.scalar_fields
import tstudio.color_fields
import tstudio.utils
from tqdm import tqdm
from PIL import Image
from pathlib import Path

def run():
    curr_path = Path(__file__).parent
    img = Image.open(curr_path / "../sunset.jpg")
    matrix_data = np.array(img, dtype=float) / 255.0
    X = matrix_data.reshape(-1, 3)
    print(X.shape)

    n_colors = [10, 20, 40]

    for n in n_colors:
        print(f"Running for n_colors = {n}")
        color_field = tstudio.color_fields.matrixcolorfield.MatrixColorField(
            min_corner=np.array([0.0, 0.0]),
            max_corner=np.array([1.0, 1.0]),
            kernel_size=0.1,
            data=matrix_data,
            n_colors=n,
            temperature=1e-1,
        )
        fig = plt.figure(figsize=(4, 4))

        n_points = 50000
        xs = np.random.rand(n_points, 2)
        colors = np.array([color_field(x) for x in tqdm(xs)])
        plt.scatter(xs[:, 0], 1-xs[:, 1], color=colors, s=4, alpha=0.5)

        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.xticks([])
        plt.yticks([])
        plt.savefig(curr_path / f"matrix_color_field_{n}.png", dpi=300)

if __name__ == "__main__":
    run()
