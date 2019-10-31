from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import json
import math
from multiprocessing import Pool

# Open the color breakdown json file
color_breakdowns_file_name = "image_with_color_breakdown.json"
color_breakdowns_file_input = open(color_breakdowns_file_name, "r")
color_breakdowns_file_text = color_breakdowns_file_input.read()
color_breakdowns_file_input.close()

# Convert to json object
color_breakdowns = json.loads(color_breakdowns_file_text)

# Get color emotions file
color_emotions_file_name = "color_emotions.json"
color_emotions_file_input = open(color_emotions_file_name, "r")
color_emotions_text = color_emotions_file_input.read()
color_emotions_file_input.close()

color_emotions = json.loads(color_emotions_text)

def identify_emotion(color, emotion_reference):
    highest_index = None
    difference = None
    for i in range(len(emotion_reference)):
        emotion = emotion_reference[i]
        emotion_color = eval(emotion["code"])
        # Convert to lab
        emotion_color = sRGBColor(emotion_color[0], emotion_color[1], emotion_color[2], is_upscaled=True)
        emotion_color = convert_color(emotion_color, LabColor)
        color_diff = delta_e_cie2000(emotion_color, color)

        if highest_index == None or difference > color_diff:
            highest_index = i
            difference = color_diff
    return emotion_reference[highest_index]["emotion"]

# Get the CIELCH of each section from color_breakds
def get_image_map(i):
    image = color_breakdowns[i[0]]
    color_breakdown = image["breakdown"]

    section_emotions = []
    for section in color_breakdown:
        section_color = sRGBColor(section["color"][0], section["color"][1], section["color"][2], is_upscaled=True)
        section_color_lab = convert_color(section_color, LabColor)
        section_emotion = identify_emotion(section_color_lab, color_emotions)
        
        subsection_emotions = []
        # Get subsection colors
        for subsection in section["subsections"]:
            subsection_color = sRGBColor(subsection["color"][0], subsection["color"][1], subsection["color"][2], is_upscaled=True)
            subsection_color_lab = convert_color(subsection_color, LabColor)
            subsection_emotion = identify_emotion(subsection_color_lab, color_emotions)

            layer_emotions = []
            # Get layer colors
            for layer in subsection["layers"]:
                layer_color = sRGBColor(layer[0], layer[1], layer[2], is_upscaled=True)
                layer_color_lab = convert_color(layer_color, LabColor)
                layer_emotion = identify_emotion(layer_color_lab, color_emotions)
                layer_emotions.append(layer_emotion)
            
            subsection_emotions.append({
                "subsection": subsection_emotion,
                "layers": layer_emotions
            })
    
        section_emotions.append({
            "section": section_emotion,
            "subsections": subsection_emotions
        })
    print("done {}".format(i[0]))
    return {
        "image_id": image["image_id"],
        "image_url": image["image_url"],
        "emotion": image["emotion"],
        "sections": section_emotions
    }

if __name__ == "__main__":
    pool = Pool(processes=30)
    image_emotions = pool.imap(get_image_map, enumerate(range(len(color_breakdowns))))
    pool.close()
    pool.join()

    # Store image emotions as an output file
    image_emotions_file_name = "image_emotion_maps.json"
    image_emotions_output = open(image_emotions_file_name, "w")
    image_emotions_text = json.dumps(list(image_emotions))
    image_emotions_output.write(image_emotions_text)
    image_emotions_output.close()