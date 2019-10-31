# Export model as ONNX Model
# Use ONNX to coreml to export the model
import torch
import os

os.chdir("../models")
model = torch.load("model.pt", map_location=torch.device('cpu'))
