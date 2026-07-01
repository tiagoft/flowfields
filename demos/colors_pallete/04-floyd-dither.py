import numpy as np
import matplotlib.pyplot as plt
import tstudio.vector_fields
import tstudio.scalar_fields
import tstudio.utils
from tqdm import tqdm
from PIL import Image
from scipy.ndimage import gaussian_filter
from pathlib import Path

from sklearn.cluster import KMeans

def floyd_steinberg_dither(matrix_data, centers):
    """
    matrix_data: array (H, W, 3) float em [0, 1]
    centers: array (n_colors, 3) - os centróides do k-means
    """
    img = matrix_data.copy().astype(float)
    h, w, _ = img.shape

    for y in range(h):
        for x in range(w):
            old_pixel = img[y, x].copy()

            # encontra o centróide mais próximo
            dists = np.sum((centers - old_pixel) ** 2, axis=1)
            idx = np.argmin(dists)
            new_pixel = centers[idx]

            img[y, x] = new_pixel
            error = old_pixel - new_pixel

            # difunde o erro (checando limites da imagem)
            if x + 1 < w:
                img[y, x + 1] += error * 7 / 16
            if x - 1 >= 0 and y + 1 < h:
                img[y + 1, x - 1] += error * 3 / 16
            if y + 1 < h:
                img[y + 1, x] += error * 5 / 16
            if x + 1 < w and y + 1 < h:
                img[y + 1, x + 1] += error * 1 / 16

    return np.clip(img, 0, 1)

def run():
    curr_path = Path(__file__).parent
    img = Image.open(curr_path / "../sunset.jpg")
    matrix_data = np.array(img, dtype=float) / 255.0
    X = matrix_data.reshape(-1, 3)
    print(X.shape)

    n_colors = [3, 10, 20]

    for n in tqdm(n_colors):
        kmeans = KMeans(n_clusters=n, random_state=0)
        kmeans.fit(X)
        centers = kmeans.cluster_centers_

        dithered_img = floyd_steinberg_dither(matrix_data, centers)

        plt.imsave(curr_path / f"sunset_kmeans_fs_{n}.png", dithered_img)

if __name__ == "__main__":
    run()
