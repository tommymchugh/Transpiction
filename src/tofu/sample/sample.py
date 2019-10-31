import torch
import torchvision
from torchvision import transforms
import cv2
import numpy as np

image = cv2.imread("Admissions_by_Zack-Laurence_Web-900x600-900x600.jpg")
image2 = cv2.imread("../../support/datasets/wikiart/raw_images/57727444edc2cb3880cb7bf6.wikiart")
image3 = cv2.imread("../../support/datasets/wikiart/raw_images/58cf89cbedc2c97b40318aae.wikiart")

image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
image = cv2.resize(image, (56, 56), interpolation = cv2.INTER_AREA)
image = transforms.ToTensor()(image)
image = image.view(1, 3, 56, 56)

image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
image2 = cv2.resize(image2, (56, 56), interpolation = cv2.INTER_AREA)
image2 = transforms.ToTensor()(image2)
image2 = image2.view(1, 3, 56, 56)

image3 = cv2.cvtColor(image3, cv2.COLOR_RGB2BGR)
image3 = cv2.resize(image3, (56, 56), interpolation = cv2.INTER_AREA)
image3 = transforms.ToTensor()(image3)
image3 = image3.view(1, 3, 56, 56)

#torchvision.utils.save_image(image, 'first.png')
#torchvision.utils.save_image(image2, 'second.png')

# Testing exported models
model = torch.load("model.pt", map_location=torch.device('cpu'))

# Retreive the latent vectors for each image
mu, log_sigma = model.encode(image)
code = model.reparameterize(mu, log_sigma)
mu2, log_sigma2 = model.encode(image2)
code2 = model.reparameterize(mu2, log_sigma2)
mu3, log_sigma3 = model.encode(image3)
code3 = model.reparameterize(mu3, log_sigma3)

# Interpolate the two vectors 
interpolation_vector = (code + code2)/2
output = model.decode(code2)
torchvision.utils.save_image(output.view(1, 3, 56, 56), 'interpolation.png')