import torch
from torch.utils.data import Dataset
from torchvision import transforms
import numpy as np
import json
from PIL import Image
import download
from tqdm import tqdm
from multiprocessing import Pool
import cv2

def get_image_channels(image):
    shape_length = len(image.shape)
    if shape_length == 2:
        return 1
    else:
        return image.shape[2]

def process_image(data):
    song = data["song"]
    gray = data["gray"]
    size = data["shape"]
    data_path = data["path"]
    index = data["i"]

    image_file_name = "{}.wikiart".format(song["id"])
    image_path = "{}/raw_images/{}".format(data_path, image_file_name)
    image = cv2.imread(image_path)
    image_channels = get_image_channels(image)

    if gray == False:
        # Not converting to gray
        # Identify non rgb images and convert them to rgb
        if image_channels == 1:
            # Image is grayscale, convert to rgb
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image_channels == 4:
            # Image is rgba remove the alpha channel
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        # Convert all images to grayscale
        if image_channels != 1:
            if image_channels == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
            else:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    resize = cv2.resize(image, size, interpolation = cv2.INTER_AREA)
    pil_image = Image.fromarray(np.uint8(resize))
    tensor = transforms.ToTensor()(pil_image)
    return tensor

class PaintPoseDatset(Dataset):
    def __init__(self, data_path, gray=False, image_shape=(28, 28), verbose=True):
        self.gray = gray
        self.image_shape = image_shape
        self.verbose = verbose

        if verbose:
            print("Downloading WikiArt Images")
        # Download image dataset if needed
        download.retrieve_images()
        if verbose:
            print("Download Complete")
            print("Loading Paintpose from storage...")
        # Get the encoded song files
        encoded_songs_file_name = "encoded_songs.json"
        encoded_songs_file_path = "{}/{}".format(data_path, encoded_songs_file_name)
        encoded_songs_input = open(encoded_songs_file_path, "r")
        encoded_songs_file_text = encoded_songs_input.read()
        encoded_songs_input.close()

        encoded_songs = json.loads(encoded_songs_file_text)
        processing_list = []
        for i in range(len(encoded_songs)):
            song = encoded_songs[i]
            processing_list.append({"path": data_path, 
                            "song": song,
                            "gray": self.gray,
                            "shape": self.image_shape,
                            "i": i})
        
        pbar = tqdm(total=len(encoded_songs))
        self.data = []
        for i in range(len(encoded_songs)):
            result = process_image(processing_list[i])
            self.data.append(result)
            pbar.update()
        """
        pool = Pool(processes=25)
        
        for i, result in enumerate(pool.imap_unordered(process_image, processing_list)):
            pbar.update()
            self.data.append(result)
        pbar.close()
        pool.close()
        pool.join()
        """
        print("Loaded Paintpose!")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        image = self.data[idx]
        return image