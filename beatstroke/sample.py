from tensorflow.keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from numpy import linspace

def generate_latent_points(latent_dim, n_samples, n_classes=10):
	# generate points in the latent space
	x_input = np.random.randn(latent_dim * n_samples)
	# reshape into a batch of inputs for the network
	z_input = x_input.reshape(n_samples, latent_dim)
	return z_input

def interpolate_points(p1, p2, n_steps=10):
	# interpolate ratios between the points
	ratios = linspace(0, 1, num=n_steps)
	# linear interpolate vectors
	vectors = list()
	for ratio in ratios:
		v = (1.0 - ratio) * p1 + ratio * p2
		vectors.append(v)
	return np.asarray(vectors)

points = generate_latent_points(100, 2)
interpolation = interpolate_points(points[0], points[1], n_steps=100)

def plot_generated_images(generator, noise):
    dim = (10, 10)
    figsize = (10,10)
    generated_images = generator.predict(noise)
    generated_images = generated_images.reshape(noise.shape[0],64,64,3)

    plt.figure(figsize=figsize)
    for i in range(generated_images.shape[0]):
        plt.subplot(dim[0], dim[1], i+1)
        plt.imshow(generated_images[i], interpolation='nearest')
        plt.axis('off')
    plt.tight_layout()
    plt.savefig('sample_generated_image.png')

generator = load_model("generator.h5")
plot_generated_images(generator, interpolation)