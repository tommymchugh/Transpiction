#
# Name: retrieve.py
# Author: Tommy McHugh
# Description: Retrieves the main emotion and the image blob of wikiarts
# Date Created: 10/15/2019

import json

# Load the image reference json file
# Import as json object
image_reference_file_name = "image_reference.json"
image_reference_input_file = open(image_reference_file_name, "r")
image_reference_file_text = image_reference_input_file.read()
image_reference_input_file.close()

image_reference = json.loads(image_reference_file_text)

# Create a method for finding the url of the image specified
def find_image_url_by_id(image_id, image_reference):
    for image_item in image_reference:
        if image_item["ID"] == image_id:
            return image_item["image"]

# Load the image emotion reference json file
# import as json object
image_emotions_file_name = "image_emotions.json"
image_emotions_input_file = open(image_emotions_file_name, "r")
image_emotions_file_text = image_emotions_input_file.read()
image_emotions_input_file.close()

image_emotions_raw = json.loads(image_emotions_file_text)
# Define the dictionary to hold the unique emotion lists for each image
image_emotions = dict() 

for image_emotion in image_emotions_raw:
    image_id = image_emotion["id"]

    # Get the existing emotion list
    # Combine it with the new emotions in this entry
    existing_emotion_list = image_emotions.get(image_id, [])
    for emotion in image_emotion["emotions"]:
        if emotion != None:
            existing_emotion_list.append(emotion)
    # Save the new list to the dictionary
    image_emotions[image_id] = existing_emotion_list

image_paired_emotion_list = list()

# Identify the maximum frequency emotion for each image
for image_id in image_emotions.keys():
    image_emotions_list = image_emotions[image_id]

    # Add the count of each emotion used
    emotions_count = dict()
    for emotion in image_emotions_list:
        emotions_count[emotion] = emotions_count.get(emotion, 0) + 1

    # Determine the maximum frequency emotion
    maximum_emotion = None
    maximum_count = -1
    for emotion in emotions_count.keys():
        count = emotions_count[emotion]
        if count > maximum_count:
            maximum_emotion = emotion
            maximum_count = count

    image_paired_emotion_list.append({"image_id": str(image_id), 
                                      "image_url": str(find_image_url_by_id(image_id, image_reference)),
                                      "emotion": str(maximum_emotion)})

# Save the data to an output json file
image_paired_emotion_json = json.dumps(image_paired_emotion_list)
file_output_name = "output.json"
file_output = open(file_output_name, "w")
file_output.write(image_paired_emotion_json)
file_output.close()