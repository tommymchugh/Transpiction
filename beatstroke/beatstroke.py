import numpy as np
import matplotlib.pyplot as plt
import tensorflow.keras
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dense, Dropout, Input, BatchNormalization, UpSampling2D, Conv2D, Reshape, Activation
from tensorflow.keras.models import Model, Sequential
from tqdm import tqdm
from tensorflow.keras.optimizers import Adam
from utils import create_dir, is_dir_empty
from multiprocessing import Pool
import json
import requests
import cv2

wikiart_painting_dir_name = "raw_images"
wikiart_painting_dir_path = "../datasets/wikiart/{}".format(wikiart_painting_dir_name)

wikiart_file_name = "wikiart"
wikiart_file_path = "../datasets/wikiart/{}.json".format(wikiart_file_name)

image_save_path = "../datasets/wikiart/{}/".format(wikiart_painting_dir_name)

def request_image_url(image_resource):
    image_id = image_resource[0]
    image_url = image_resource[1]

    # Get the requested image
    # Set verify to false because SSL sometimes is bad on wikiart
    response = requests.get(image_url, verify=False)
    image_data = response.content

    # Save the image data to a file
    image_path = "{}{}.wikiart".format(image_save_path, image_id)
    image_output = open(image_path, "wb")
    image_output.write(image_data)
    image_output.close()
    print("Saved image: {}".format(image_id))
    return True

def retrieve_images():
    # Determine if art resource file is empty
    # Load all paintings if it is
    # Create the directory if it doesn't already exist
    create_dir(wikiart_painting_dir_path) 

    if is_dir_empty(wikiart_painting_dir_path) == True:
        # Raw images not download
        # Retrieve all the image links and download them
        # Load wikiart dataset as object from json
        wikiart_file_input = open(wikiart_file_path, "r")
        wikiart_file_text = wikiart_file_input.read()
        wikiart_file_input.close()
        wikiart = json.loads(wikiart_file_text)

        # Store the image urls as a saved array
        request_urls = []
        for image in wikiart:
            image_id = image["image"]["image_id"]
            image_url = image["image"]["image_url"]
            request_urls.append((image_id, image_url))

        # Request async processing of urls
        pool = Pool(processes=25)
        pool.map(request_image_url, request_urls)
        pool.close()
        pool.join()

if __name__ == "__main__":
    # Retrieve dataset if necessary
    retrieve_images()

    # Get the encoded song files
    encoded_songs_file_name = "encoded_songs.json"
    encoded_songs_file_path = "../datasets/wikiart/{}".format(encoded_songs_file_name)
    encoded_songs_input = open(encoded_songs_file_path, "r")
    encoded_songs_file_text = encoded_songs_input.read()
    encoded_songs_input.close()

    encoded_songs = json.loads(encoded_songs_file_text)

    songs = []
    images = []

    testing_songs = []

    for i in range(len(encoded_songs)):
        print(i)
        song = encoded_songs[i]
        image_file_name = "{}.wikiart".format(song["id"])
        image_path = "../datasets/wikiart/raw_images/{}".format(image_file_name)

        image = cv2.imread(image_path)
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            if image.shape[2] == 4:
                # Convert rgba to rgb
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        image = cv2.resize(image, (64, 64)) / 255
        songs.append(np.asarray(song["pitches"]))
        images.append(image)
     
    songs = np.asarray(songs)
    images = np.asarray(images)

    def adam_optimizer():
        return Adam(lr=0.0002, beta_1=0.5)
    
    def create_generator():
        generator=Sequential()
        dropout_prob = 0.4
        
        generator.add(Dense(8*8*256, input_dim=100))
        generator.add(BatchNormalization(momentum=0.8))
        generator.add(Activation('relu'))
        generator.add(Reshape((8,8,256)))
        generator.add(Dropout(dropout_prob))
        
        generator.add(UpSampling2D())
        generator.add(Conv2D(128, 5, padding='same'))
        generator.add(BatchNormalization(momentum=0.8))
        generator.add(Activation('relu'))
        
        generator.add(UpSampling2D())
        generator.add(Conv2D(128, 5, padding='same'))
        generator.add(BatchNormalization(momentum=0.8))
        generator.add(Activation('relu'))
        
        generator.add(UpSampling2D())
        generator.add(Conv2D(64, 5, padding='same'))
        generator.add(BatchNormalization(momentum=0.8))
        generator.add(Activation('relu'))
        
        generator.add(Conv2D(32, 5, padding='same'))
        generator.add(BatchNormalization(momentum=0.8))
        generator.add(Activation('relu'))
        
        generator.add(Conv2D(3, 5, padding='same'))
        generator.add(Activation('tanh'))
        
        generator.compile(loss='binary_crossentropy', optimizer=adam_optimizer())
        return generator

    generator = create_generator()
    generator.summary()

    def create_discriminator():
        discriminator = Sequential()
        dropout_prob = 0.4
        discriminator.add(tf.keras.layers.Conv2D(64, 5, strides=2, input_shape=(64, 64, 3), padding='same'))
        discriminator.add(tf.keras.layers.LeakyReLU())
        discriminator.add(tf.keras.layers.Dropout(dropout_prob))
        
        discriminator.add(tf.keras.layers.Conv2D(128, 5, strides=2, padding='same'))
        discriminator.add(BatchNormalization(momentum=0.8))
        discriminator.add(tf.keras.layers.LeakyReLU())
        discriminator.add(tf.keras.layers.Dropout(dropout_prob))
        
        discriminator.add(tf.keras.layers.Conv2D(256, 5, strides=2, padding='same'))
        discriminator.add(BatchNormalization(momentum=0.8))
        discriminator.add(tf.keras.layers.LeakyReLU())
        discriminator.add(tf.keras.layers.Dropout(dropout_prob))
        
        discriminator.add(tf.keras.layers.Conv2D(512, 5, strides=2, padding='same'))
        discriminator.add(BatchNormalization(momentum=0.8))
        discriminator.add(tf.keras.layers.LeakyReLU())
        discriminator.add(tf.keras.layers.Dropout(dropout_prob))
        
        discriminator.add(tf.keras.layers.Flatten())
        discriminator.add(tf.keras.layers.Dense(1))
        discriminator.add(tf.keras.layers.Activation('sigmoid'))
        
        discriminator.compile(loss='binary_crossentropy', optimizer=adam_optimizer())
        return discriminator
    discriminator =create_discriminator()
    discriminator.summary()

    def create_gan(discriminator, generator):
        discriminator.trainable=False
        gan_input = Input(shape=(100,))
        x = generator(gan_input)
        gan_output= discriminator(x)
        gan= Model(inputs=gan_input, outputs=gan_output)
        gan.compile(loss='binary_crossentropy', optimizer='adam')
        return gan
    gan = create_gan(discriminator,generator)
    gan.summary()

    def plot_generated_images(epoch, generator, examples=100, dim=(10,10), figsize=(10,10)):
        noise= np.random.normal(loc=0, scale=1, size=[examples, 100])
        generated_images = generator.predict(noise)
        generated_images = generated_images.reshape(100,64,64,3)

        plt.figure(figsize=figsize)
        for i in range(generated_images.shape[0]):
            plt.subplot(dim[0], dim[1], i+1)
            plt.imshow(generated_images[i], interpolation='nearest')
            plt.axis('off')
        plt.tight_layout()
        plt.savefig('gan_generated_image %d.png' %epoch)

    def training(epochs=1, batch_size=100):
        #Loading the data
        batch_count = images.shape[0] // batch_size
        
        # Creating GAN
        generator= create_generator()
        discriminator= create_discriminator()
        gan = create_gan(discriminator, generator)
        
        for e in range(1,epochs+1 ):
            print("Epoch %d" %e)
            for i in tqdm(range(len(images) // batch_size)):
                #generate  random noise as an input  to  initialize the  generator
                noise= np.random.normal(0,1, [batch_size, 100])
                # Generate fake MNIST images from noised input
                generated_images = generator.predict(noise)
                
                # Get a random set of  real images
                image_batch = images[(i*batch_size):(i*batch_size)+batch_size]

                #Construct different batches of  real and fake data 
                X= np.concatenate([image_batch, generated_images])
                
                # Labels for generated and real data
                y_dis=np.zeros(2*batch_size)
                y_dis[:batch_size]=1.0
                
                #Pre train discriminator on  fake and real data  before starting the gan. 
                discriminator.trainable=True
                discriminator.train_on_batch(X, y_dis)
                
                #Tricking the noised input of the Generator as real data
                noise= np.random.normal(0,1, [batch_size, 100])
                y_gen = np.ones(batch_size)
                
                # During the training of gan, 
                # the weights of discriminator should be fixed. 
                #We can enforce that by setting the trainable flag
                discriminator.trainable=False
                
                #training  the GAN by alternating the training of the Discriminator 
                #and training the chained GAN model with Discriminator’s weights freezed.
                gan.train_on_batch(noise, y_gen)
            if e % 50 == 0:
                generator.save("generator-{}.h5".format(e))
            if e == 1 or e % 20 == 0:
                plot_generated_images(e, generator)
        generator.save("generator.h5")
        gan.save("gan.h5")
    training(750,32)


