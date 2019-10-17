import tensorflow as tf
import numpy as np
import math
import matplotlib.pyplot as plt
import cv2

# Define the recovery optimizer
optimizer = tf.keras.optimizers.SGD(lr=0.2, decay=0.0000006)

# Load the art generator model
generator = tf.keras.models.load_model("generator.h5")

class Recover:
    def __init__(self, wikiart_id):
        # Load the specific recovered seeking image
        self.wikiart_id = wikiart_id
        file_path = "../datasets/wikiart/raw_images/{}.wikiart".format(wikiart_id)
        self.image = cv2.imread(file_path)

        # Resize it to fit input
        if len(image.shape) == 2:
            self.image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            if image.shape[2] == 4:
                # Convert rgba to rgb
                self.image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        self.image = cv2.resize(image, (64, 64)) / 255
        self.image = np.asarray([image])
        self.image_input = tf.keras.backend.constant(image, dtype="float32")

        # Create a random starting point of noise
        noise_potential_count = 100
        noise_potentials = np.random.normal(loc=0, scale=1, size=(noise_potential_count, 100,))
        # Find the noise with the lowest error
        # make that the starting noise
        losses = []
        for i in range(noise_potentials.shape[0]):
            loss = (np.square(image_input - generator(np.asarray([noise_potentials[i]])))).mean(axis=None)
            losses.append(loss)
        losses = np.asarray(losses)
        min_index = np.argmin(losses)
        print("Identified min index as {}".format(min_index))
        noise = np.asarray(noise_potentials[min_index])
        self.noise_output = tf.keras.backend.variable(noise.reshape(1, 100, ), dtype="float32")
    
    def get_latent_vector(self, min_threshold=0.01, max_iter=75000 verbose=True, save_images=(True, 10000)):
        # Define model loss function
        global_loss = -1
        def loss():
            global global_loss
            global_loss = tf.math.reduce_mean(tf.math.squared_difference(image_input, generator(noise_output)))
            return global_loss

        # Define constant threshold to stop at
        threshold = tf.keras.backend.constant(min_threshold, dtype="float32")

        # Iterate through gradient descent
        # Minimize the mse for the generated noise
        if verbose:
            print("Starting iteration process")

        if save_images[0] == True:
            first_image = image.reshape(64,64,3)
            plt.imshow(first_image, interpolation='nearest')
            plt.savefig('sample_generated_image-first.png')

        optimizer.minimize(loss, var_list=[self.noise_output])
        iteration = 1
        while tf.math.greater_equal(global_loss, threshold) == True or iteration >= max_iter:
            optimizer.minimize(loss, var_list=[self.noise_output])
            if verbose:
                print("Iter: {} - {}".format(iteration, global_loss))

            if save_images[0] == True:
                if iteration % save_images[1] == 0 or iteration == 1:
                    new_image = generator.predict(self.noise_output)
                    new_image = new_image.reshape(64,64,3)

                    plt.imshow(new_image, interpolation='nearest')
                    plt.savefig('sample_generated_image-{}.png'.format(iteration))
            iteration += 1
        return self.noise_output

# Load a starry night
starry_night_id = "5772716cedc2cb3880c1907f"
starry_night = Recover(starry_night_id)
print(starry_night.get_latent_vector())