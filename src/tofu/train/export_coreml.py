# Export model as ONNX Model
# Use ONNX to coreml to export the model
import torch
import torch.nn as nn
import os
import onnx
from onnx_tf.backend import prepare
import tofu
from onnx_coreml import convert

# Import the existing model
os.chdir("../models")

model = torch.load("model.pt", map_location=torch.device('cpu'))
scripted_model = torch.jit.script(model)
# Create a simple decoder class
class TofuDecoder(nn.Module):
    def __init__(self):
        super(TofuDecoder, self).__init__()
        self.tofu = model
        super(TofuDecoder, self).add_module("Tofu", self.tofu)
    
    def forward(self, input_layer):
        return self.tofu.decode(input_layer)

# Create random noise
device = torch.device("cpu")
noise = torch.randn(1, 100).to(device, dtype=torch.float)

decoder = TofuDecoder()
decoder = decoder.to(device)

torch.onnx.export(decoder, 
                noise, 
                "onnx/model.onnx", 
                input_names=["latent_vector"],
                output_names=["image"],
                dynamic_axes={'latent_vector' : {0 : [1, 100]}, 'image' : {0 : [1, 3, 56, 56]}})

coreml_model = convert(model="onnx/model.onnx", target_ios='13')
coreml_model.save("coreml/tofu.mlmodel")