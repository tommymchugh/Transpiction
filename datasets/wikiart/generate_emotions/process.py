#
# Name: process.py
# Author: Tommy McHugh
# Description: Processes the collected images to determine a feeling score for the image
# Date Created: 10/15/2019

import json
from PIL import Image
from io import BytesIO
import math
from multiprocessing import Pool

# Define how many sections and sub sections will be present
sections = 4
sub_sections = 4
viewing_size = 2

# Import the image emotion reference
# store as json object
image_emotions_file_name = "image_with_paired_emotion.json"
image_emotions_input = open(image_emotions_file_name, "r")
image_emotions_text = image_emotions_input.read()
image_emotions_input.close()

image_emotions = json.loads(image_emotions_text)

image_colors = []

# For each image
def store_image_colors(tuple_value):
    image_item = image_emotions[tuple_value[0]]
    image_feeling_list = list()

    # Get the image
    image_file_name = "images/{}.wikiart".format(image_item["image_id"])
    image_file = open(image_file_name, "r")
    image_file_text = image_file.read()
    image_file.close()

    image = Image.open(BytesIO(image_file_text))
    image_pixels = image.load()
    image_size = image.size
    image_width = image_size[0]
    image_height = image_size[1]

    # Break down image into sections and sub sections
    image_color_breakdown = []
    section_width = int(math.floor(image_width/sections))
    for section in range(sections):
        image_color_breakdown.append({
            "type": "section",
            "subsections": []
        })
        # Define the pixel bounds for the section
        start_pixel = section*section_width
        if section > 0:
            start_pixel += 1
        end_pixel = (section+1)*section_width

        # Define the pixel bounds for the sub sections
        subsection_width_num = int(math.floor(sub_sections/2))
        subsection_height_num = int(math.floor(sub_sections/2))

        subsection_width = int(math.floor((end_pixel-start_pixel)/subsection_width_num))
        subsection_height = int(math.floor(image_height/subsection_height_num))

        subsection_items = [list(range(2)) for _ in range(2)]
        subsection_colors = []
        for row in range(len(subsection_items)):
            row_items = subsection_items[row]
            for subsection in row_items:
                image_color_breakdown[section]["subsections"].append({
                    "type": "subsection",
                    "layers": []
                })
                subsection_start_pixel_x= start_pixel+(subsection*subsection_width)
                subsection_start_pixel_y = row*subsection_height
                if subsection > 0:
                    subsection_start_pixel_x += 1

                subsection_end_pixel_x = start_pixel+((subsection+1)*subsection_width)
                subsection_end_pixel_y = row*subsection_height

                # Break subsections into pixel layers
                layer_colors = []
                for layer_num in range(int(math.floor(subsection_width/viewing_size))):
                    layer_start_pixel_x = subsection_start_pixel_x+(viewing_size*layer_num)
                    layer_start_pixel_y = subsection_start_pixel_y

                    if layer_num > 0:
                        layer_start_pixel_x += 1

                    layer_end_pixel_x = layer_start_pixel_x + viewing_size
                    layer_end_pixel_y = subsection_start_pixel_y

                    # Get the layer pixels
                    pixel_count = 0
                    red = 0
                    green = 0
                    blue = 0

                    for pixel_width_index in range(layer_end_pixel_x-layer_start_pixel_x):
                        pixel_x = layer_start_pixel_x + pixel_width_index
                        if pixel_x < image_width:
                            for pixel_height_index in range(subsection_height):
                                pixel_y = layer_start_pixel_y+pixel_height_index

                                if pixel_y < image_height:
                                    try:
                                        pixel = image_pixels[pixel_x, pixel_y]

                                        if isinstance(pixel, int) == True:
                                            # Convert pixel to 3 channel
                                            pixel = (pixel, pixel, pixel)

                                        red += pixel[0] * pixel[0]
                                        green += pixel[1] * pixel[1]
                                        blue += pixel[2] * pixel[2]
                                        pixel_count += 1
                                    except:
                                        print("error")
                    if pixel_count > 0:
                        red = int(math.floor(math.sqrt(red/pixel_count)))
                        green = int(math.floor(math.sqrt(green/pixel_count)))
                        blue = int(math.floor(math.sqrt(blue/pixel_count)))
                        image_color_breakdown[section]["subsections"][(2*row)+subsection]["layers"].append((red, green, blue))
                pixel_count = 0
                red = 0
                green = 0
                blue = 0
                for pixel in image_color_breakdown[section]["subsections"][(2*row)+subsection]["layers"]:
                    red += pixel[0]*pixel[0]
                    green += pixel[1]*pixel[1]
                    blue += pixel[2]*pixel[2]
                    pixel_count += 1
                red = int(math.floor(math.sqrt(red/pixel_count)))
                green =int(math.floor(math.sqrt(green/pixel_count)))
                blue = int(math.floor(math.sqrt(blue / pixel_count)))
                subsection_color = (red, green, blue)
                subsection_colors.append(subsection_color)
                image_color_breakdown[section]["subsections"][(2*row)+subsection]["color"] = subsection_color
        pixel_count = 0
        red = 0
        green = 0
        blue = 0
        for pixel in subsection_colors:
            red += pixel[0]*pixel[0]
            green += pixel[1]*pixel[1]
            blue += pixel[2]*pixel[2]
            pixel_count += 1
        red = int(math.floor(math.sqrt(red/pixel_count)))
        green = int(math.floor(math.sqrt(green/pixel_count)))
        blue = int(math.floor(math.sqrt(blue/pixel_count)))
        section_color = (red, green, blue)
        image_color_breakdown[section]["color"] = section_color
    print("done {}".format(tuple_value[0]))
    return {
        "image_url": image_item["image_url"],
        "image_id": image_item["image_id"],
        "emotion": image_item["emotion"],
        "breakdown": image_color_breakdown
    }

if __name__ == "__main__":
    pool = Pool(processes=25)
    image_colors = pool.imap(store_image_colors, enumerate(range(len(image_emotions))))
    pool.close()
    pool.join()

    image_colors_json_text = json.dumps(list(image_colors))
    file_output_name = "image_with_color_breakdown.json"
    file_output = open(file_output_name, "w")
    file_output.write(image_colors_json_text)
    file_output.close()
