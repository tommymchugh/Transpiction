import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms
from tqdm import tqdm
import torchvision
import sys
import math
import utils
import matplotlib.pyplot as plt

class Tofu(nn.Module):
    def __init__(self, input_shape=(28,28), epochs=20000, batch_size=32, ls_dim=2):
        super(Tofu, self).__init__()
        self.epochs = epochs
        self.batch_size = batch_size
        self.input_shape = input_shape
        self.latent_space_dims = ls_dim

        # Define encoder layers neuron counts
        encoder_input_nc = 256

        # Create encoder layers
        self.encoder_input = nn.Conv2d(3, 32, kernel_size=(3, 3))
        self.encoder_input_pool = nn.MaxPool2d((2, 2))
        self.encoder_h1 = nn.Conv2d(32, 64, kernel_size=(3, 3))
        self.encoder_h1_pool = nn.MaxPool2d((2, 2))
        self.encoder_h2 = nn.Conv2d(64, 32, kernel_size=(3, 3))
        self.encoder_h2_pool = nn.MaxPool2d((2, 2))
        self.encoder_flatten = nn.Flatten()
        self.encoder_mu = nn.Linear(800, self.latent_space_dims)
        self.encoder_output = nn.Linear(ls_dim, ls_dim)

        # Define decoder layers neuron counts
        decoder_input_nc = 256
        decoder_output_nc = 784

        # Create decoder layers
        deconvolution_input_output_size = int(((input_shape[0]/4)-1)*((input_shape[1]/4)-1)*32)
        self.decoder_input = nn.Linear(self.latent_space_dims, deconvolution_input_output_size)
        self.decoder_h1 = nn.ConvTranspose2d(32, 64, kernel_size=3, stride=(2, 2), output_padding=0)
        self.decoder_h2 = nn.ConvTranspose2d(64, 3, kernel_size=3, stride=(2, 2), output_padding=1)
        self.decoder_output = nn.ConvTranspose2d(32, 3, kernel_size=3, stride=1, output_padding=0)

    def encode(self, layer_input):
        # Conv2d input with a relu activation
        layer_input = F.relu(self.encoder_input(layer_input))
        layer_input = self.encoder_input_pool(layer_input)

        # Conv2d hidden layer with relu activation
        layer_input = F.relu(self.encoder_h1(layer_input))
        layer_input = self.encoder_h1_pool(layer_input)

        layer_input = F.relu(self.encoder_h2(layer_input))
        layer_input = self.encoder_h2_pool(layer_input)

        # Flatten layer
        layer_input = self.encoder_flatten(layer_input)
        gaussian_param_mu = self.encoder_mu(layer_input)
        
        # Convolutional output
        gaussian_param_log_sigma = self.encoder_output(gaussian_param_mu)
        return gaussian_param_mu, gaussian_param_log_sigma

    def decode(self, layer_input):
        # Dense input layer with relu activation
        layer_input = F.relu(self.decoder_input(layer_input))
        # Reshape flat layer
        layer_input = layer_input.view(layer_input.size()[0], 32, int(self.input_shape[0]/4)-1, int(self.input_shape[1]/4)-1)
        # Perform deconvolutions with 2 stride
        layer_input = F.relu(self.decoder_h1(layer_input))
        layer_input = torch.sigmoid(self.decoder_h2(layer_input))
        return layer_input

    def reparameterize(self, mu, log_sigma):
        # Gaussian sample of encoded rep of input
        std = torch.exp(log_sigma / 2)
        eps = torch.randn_like(std)
        return mu + std * eps

    def __reshape_input_flat(self, input_item):
        rows = -1 # Unsure of the total row count
        cols = self.input_shape[0]**2
        reshaped_input = input_item.view(rows, cols)
        return reshaped_input
    
    def __reshape_input_multi(self, input_item):
        rows = -1 # Unsure of the total row count
        reshaped_input = input_item.view(rows, self.input_shape[0], self.input_shape[1])
        return reshaped_input

    def forward(self, layer_input):
        # Encode the reshaped input
        mu, log_sigma = self.encode(layer_input)
        # Use reparameterization trick to calculate encoded rep
        z_encoded_rep = self.reparameterize(mu, log_sigma) # Returns sample z ~ Gaussian Sample z|X = Q(z|X)
        # Decode the encoded rep
        decoding = self.decode(z_encoded_rep)
        return decoding, mu, log_sigma, z_encoded_rep

    def __setup_model(self):
        # Set the learning for the model optimizer
        learning_rate = 1e-3
        # Get the optimizer for the model
        # Store locally to
        model_optimizer = optim.Adam(self.parameters(), lr=learning_rate)

        # Check to see if GPU access is available
        if self.__gpu_is_available():
            training_device_type = "cuda"
        else:
            training_device_type = "cpu"
        print("Using Device Type: {}".format(training_device_type))
        training_device = torch.device(training_device_type)

        # Return model converted to runnable on training device
        device_model = self.to(training_device)

        return device_model, model_optimizer, training_device

    def __train(self, model, optimizer, device, epoch):
        model.train()
        train_loss = 0

        for batch_index, training_data in tqdm(enumerate(self.train_loader), total=len(self.dataset) // self.batch_size):
            # Send the training data to the gpu
            training_data = training_data.to(device, dtype=torch.float)
            optimizer.zero_grad()
            prediction, mu, log_sigma, z_rep = model(training_data)
            loss = self.__vae_loss(training_data, prediction, log_sigma, mu)
            loss.backward()

            train_loss += loss.item()
            optimizer.step()
        
        avg_loss = train_loss / len(self.train_loader.dataset)
        print('====> Epoch: {} Average loss: {}'.format(epoch, avg_loss))

    def __gpu_is_available(self):
        return torch.cuda.is_available()

    def __vae_loss(self, y_true, y_pred, log_sigma, mu):
        # Reshape to fit the correct size of eachother
        y_pred = y_pred
        #print(y_pred.size())
        y_true = y_true
        #print(y_pred.size())

        # Calculate the reconstruction loss
        reconstruction_loss = F.binary_cross_entropy(y_pred, y_true, reduction='sum')

        # Calculate the KL loss
        kl_loss = -0.5 * torch.sum(1 + log_sigma - mu.pow(2) - log_sigma.exp())
        return reconstruction_loss + kl_loss

    def load_data(self, dataset):
        kwargs = {'num_workers': 1, 'pin_memory': True} if self.__gpu_is_available() else {}
        self.dataset = dataset
        self.train_loader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True, **kwargs)

    def train_model(self, verbose=True, save_image=(True, 20)):
        # Setup the device model, optimizer, and device type
        model, optimizer, device = self.__setup_model()
        utils.create_dir("training_results")

        for batch_index, training_data in tqdm(enumerate(self.train_loader), total=len(self.dataset) // self.batch_size):
            if batch_index == 120:
                torchvision.utils.save_image(training_data, 'training_results/sample.png')
                break
        # Save an example
        # Start training model
        for epoch in range(self.epochs):
            print("Starting Epoch: {}".format(epoch))
            self.__train(model, optimizer, device, epoch+1)

            if epoch % save_image[1] == 0 or epoch == 1:
                with torch.no_grad():
                    sample = torch.randn(64, self.latent_space_dims).to(device, dtype=torch.float)
                    sample = model.decode(sample).cpu()
                    torchvision.utils.save_image(sample.view(-1, 3, 56, 56), 'training_results/sample_{}.png'.format(epoch))

            if epoch % 500 == 0:
                torch.save(model, "model-{}.pt".format(epoch))
        torch.save(model, "model.pt")