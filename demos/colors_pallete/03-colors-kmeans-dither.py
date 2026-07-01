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


def _kernel(y, sigma):
    return np.exp(-0.5 * (y ** 2) / (sigma ** 2))

def run():
    curr_path = Path(__file__).parent
    img = Image.open(curr_path / "../sunset.jpg")
    matrix_data = np.array(img, dtype=float) / 255.0
    X = matrix_data.reshape(-1, 3)
    print(X.shape)



    n_colors = [3, 10, 20]
    # K-Means
    for n in tqdm(n_colors):
        kmeans = KMeans(n_clusters=n, random_state=0)
        kmeans.fit(X)
        
        y = kmeans.transform(X)
        
        centers = kmeans.cluster_centers_
        sigma = 0.1  # Adjust this value to control the amount of dithering
        
        y_prob = _kernel(y, sigma)
        y_prob_norm = y_prob / np.sum(y_prob, axis=1, keepdims=True)
        labels = []
        for i in range(X.shape[0]):
            labels.append(np.random.choice(n, p=y_prob_norm[i]))

        # Create a new image with the clustered colors
        clustered_img = centers[labels].reshape(matrix_data.shape)

        # Save the clustered image
        plt.imsave(curr_path / f"sunset_kmeans_dither_{n}.png", clustered_img)

if __name__ == "__main__":
    run()
