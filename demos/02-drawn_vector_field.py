import numpy as np
import matplotlib.pyplot as plt
import tstudio.vector_fields
import tstudio.scalar_fields
import tstudio.utils
from tqdm import tqdm

def run():
    field1 = tstudio.vector_fields.RotationField(np.array([1, 1]), normalize=False)
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
        normalize=False,
    )

    xlim = (-3, 3)
    ylim = (-3, 3)

    n_lines = 10000
    scale = 5e-1
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
        
        X.append([x, x+scale*vector[0]])
        Y.append([y, y+scale*vector[1]])

    X = np.array(X)
    Y = np.array(Y)
    plt.figure(figsize=(6, 6))
    plt.plot(X.T, Y.T, color='#0f4521', alpha=0.1)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xticks([])
    plt.yticks([])
    #plt.title("Simple Vector Field")
    plt.savefig("02-drawn_vector_field.png")
    plt.show()
    
if __name__ == "__main__":
    run()