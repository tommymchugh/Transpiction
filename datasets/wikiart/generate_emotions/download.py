import requests
import json
from multiprocessing import Pool

# Open image json file
image_emotions_file_name = "image_with_paired_emotion.json"
image_emotions_file_input = open(image_emotions_file_name, "r")
image_emotions_file_text = image_emotions_file_input.read()
image_emotions_file_input.close()

# Convert to json object
image_emotions = json.loads(image_emotions_file_text)

# Get the image and save to a file
def save_image(image):
    response = requests.get(image["image_url"], verify=False)
    content = response.content

    # Save image content
    output_file_name = "images/{}.wikiart".format(image["image_id"])
    output_file = open(output_file_name, "wb")
    output_file.write(content)
    output_file.close()
    return True

if __name__ == "__main__":
    pool = Pool(processes=50)
    responses = pool.map(save_image, image_emotions)
