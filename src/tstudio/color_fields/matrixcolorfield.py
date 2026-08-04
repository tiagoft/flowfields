#from tstudio.color_fields.base import ColorField
import numpy as np
from sklearn.cluster import KMeans


class MatrixColorField():
    """
    A color field that is defined by a matrix of colors.
    """

    def __init__(
        self,
        min_corner: np.ndarray,
        max_corner: np.ndarray,
        data: np.ndarray,
        n_colors: int,
        random_state: int = 0,
        kernel_size: float = 0.05,
        temperature: float = 1.0,
    ):
        super().__init__()
        self.min_corner = min_corner
        self.max_corner = max_corner
        self.data = data
        self.n_colors = n_colors
        self.random_state = random_state
        self.kernel_size = kernel_size
        self.temperature = temperature

        # Perform k-means clustering to find the n_colors most representative colors
        self.kmeans = KMeans(
            n_clusters=self.n_colors,
            random_state=self.random_state,
        )
        self.kmeans.fit(self.data.reshape(-1, 3))

        # Classify every pixel once and build one integral image (2D prefix
        # sum) per cluster, so windowed pixel counts can be looked up in
        # O(1) instead of reclassifying pixels on every get_probs call.
        h, w, _ = self.data.shape
        labels = self.kmeans.predict(self.data.reshape(-1, 3)).reshape(h, w)
        self.integral_images = np.zeros((self.n_colors, h + 1, w + 1), dtype=np.int32)
        for k in range(self.n_colors):
            mask = labels == k
            self.integral_images[k, 1:, 1:] = mask.cumsum(axis=0).cumsum(axis=1)

    def get_probs(self, x: np.ndarray) -> np.ndarray:

        # Get the normalized coordinates of x in the range [0, 1]
        t = (x - self.min_corner) / (self.max_corner - self.min_corner)
        t = np.clip(t, 0.0, 1.0)



        # Select a window from the data matrix based on the kernel size
        h, w, _ = self.data.shape
        center_x = int(t[0] * (w-1))
        center_y = int(t[1] * (h-1))
        half_k = int(self.kernel_size * max(w, h) / 2)
        x_min = max(center_x - half_k, 0)
        x_max = min(center_x + half_k + 1, w)
        y_min = max(center_y - half_k, 0)
        y_max = min(center_y + half_k + 1, h)
        #print(y_min, y_max, x_min, x_max)

        # Count the number of pixels closest to each cluster center within the
        # window via an O(1) integral-image box-sum lookup.
        count = (
            self.integral_images[:, y_max, x_max]
            - self.integral_images[:, y_min, x_max]
            - self.integral_images[:, y_max, x_min]
            + self.integral_images[:, y_min, x_min]
        ).astype(float)

        z = count
        z = z.clip(min=1)
        z = z / z.sum()  # Normalize to get probabilities
        probs = np.exp(z / self.temperature)
        probs /= probs.sum()  # Normalize to get probabilities 
        
        # if probs contain NaN, print z and probs
        if np.isnan(probs).any():
            print("NaN values found in probabilities.")
            print("Count:", count)
            print("z:", z)
            print("probs:", probs)
            raise ValueError("NaN values found in probabilities.")
                             
        return probs
    
            
    def __call__(self, x: np.ndarray, random_state: int = 0) -> np.ndarray:
        probs = self.get_probs(x)
        sample = np.random.choice(list(range(self.n_colors)), p=probs.flatten())
        return self.kmeans.cluster_centers_[sample]