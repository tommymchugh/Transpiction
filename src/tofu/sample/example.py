import sys
import numpy as np
import json
import torch
import torchvision
from torchvision import transforms
import cv2

# Testing exported models
model = torch.load("tofu/model.pt", map_location=torch.device('cpu'))

input_string = sys.argv[1]
music_list = eval(input_string)
music_matrix = np.asarray(music_list).astype(np.float32)
music_matrix = np.delete(music_matrix, 0, 1)

encoded_songs_file = "datasets/wikiart/encoded_songs.json"
encoded_songs_input = open(encoded_songs_file)
encoded_songs_text = encoded_songs_input.read()
encoded_songs_input.close()

encoded_songs = json.loads(encoded_songs_text)
diffs = []
for song in encoded_songs:
    pitches_lists = song["pitches"]
    pitches_matrix = np.asarray(pitches_lists)
    pitches_matrix = np.delete(pitches_matrix, 0, 1)

    pitches_matrix_frequency = pitches_matrix[:,1]
    used_notes =
    for i in range(len(pitches_matrix_frequency)):


    difference = (np.square(pitches_matrix - music_matrix)).mean(axis=None)
    diffs.append(difference)

min_ids = []
for i in range(1):
    min_value = min(diffs)
    min_index = diffs.index(min_value)
    min_ids.append((encoded_songs[min_index]["id"], min_value))
    del diffs[min_index]

interpolation = None
started = False
total_error = 0
for painting in min_ids:
    total_error += painting[1]

for painting in min_ids:
    painting_file = "datasets/wikiart/raw_images/{}.wikiart".format(painting[0])
    image = cv2.imread(painting_file)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (56, 56), interpolation = cv2.INTER_AREA)
    image = transforms.ToTensor()(image)
    image = image.view(1, 3, 56, 56)

    mu, log_sigma = model.encode(image)
    code = model.reparameterize(mu, log_sigma)
    normalized_error = painting[1]/total_error
    lv_comp = code*normalized_error
    if started == False:
        interpolation = lv_comp
        started = True
    else:
        interpolation += lv_comp

output = model.decode(interpolation)
torchvision.utils.save_image(output.view(1, 3, 56, 56), 'interpolation.png')
print("Completed!")

