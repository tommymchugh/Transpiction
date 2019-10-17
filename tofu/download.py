from utils import create_dir, is_dir_empty
from multiprocessing import Pool
import json
import requests

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