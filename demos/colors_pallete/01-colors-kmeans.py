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

def run():
    curr_path = Path(__file__).parent
    img = Image.open(curr_path / "sunset.jpg")
    matrix_data = np.array(img, dtype=float) / 255.0
    X = matrix_data.reshape(-1, 3)
    print(X.shape)

    n_colors = [3, 10, 20]
    # K-Means
    for n in tqdm(n_colors):
        kmeans = KMeans(n_clusters=n, random_state=0)
        kmeans.fit(X)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_

        # Create a new image with the clustered colors
        clustered_img = centers[labels].reshape(matrix_data.shape)

        # Save the clustered image
        plt.imsave(curr_path / f"sunset_kmeans_{n}.png", clustered_img)

if __name__ == "__main__":
    run()
