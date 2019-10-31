# Export model as Torchscript
import torch
import os

os.chdir("../models")

# Load the pytorch model
model = torch.load("model.pt", map_location=torch.device('cpu'))
# Create random noise
device = torch.device("cpu")
noise = torch.randn(1, 100).to(device, dtype=torch.float)
# Trace noise through the decoder
scripted_model = torch.jit.script(model)

try:
    os.mkdir("mobile")
except:
    pass
scripted_model.save('mobile/tofu.zip')