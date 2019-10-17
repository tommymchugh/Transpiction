import torch
import torchvision
from torchvision import transforms
import cv2
import numpy as np

image = cv2.imread("../datasets/wikiart/raw_images/5a5da69dedc2c973d42ff2ee.wikiart")
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
image = cv2.resize(image, (56, 56), interpolation = cv2.INTER_AREA)
image = transforms.ToTensor()(image)
image = image.view(1, 3, 56, 56)

# Testing exported models
model = torch.load("model.pt")

mu, log_sigma = model.encode(image)
code = model.reparameterize(mu, log_sigma)
print(code)

output = model.decode(code)
torchvision.utils.save_image(output.view(1, 3, 56, 56), 'training_results/sample.png')