from emotion import Emotion
from utils import run_on_each_layer
import operator
import math
import random

MUSIC_KEY_MAJOR = 0
MUSIC_KEY_MINOR = 1

c_major_pitch_consonance = [0, 7, 4, 9, 2, 5, 11]
c_minor_pitch_consonance = [0, 7, 3, 8, 2, 5, 10]

note_types = {
    "whole": 0,
    "half": 1,
    "quarter": 2,
    "eigth": 3,
    "sixteenth": 4
}

melody_templates = [
    [note_types["whole"] for i in range(1)],
    [note_types["half"] for i in range(2)],
    [note_types["quarter"] for i in range(4)],
    [note_types["eigth"] for i in range(8)],
    [note_types["sixteenth"] for i in range(16)]
]

class Image:
    def __init__(self, image, positive_emotions, negative_emotions, act_max, act_min, js_max=1, js_min=0):
        self.__positive_emotions = positive_emotions
        self.__negative_emotions = negative_emotions
        self.__image_details = image
        self.__base_emotion = Emotion(image["emotion"])

        # Define the number of positive and negative emotions in the image map
        self.__positive_count = 0
        self.__negative_count = 0

        # Define the count of each emotion in the image
        self.__emotion_count = dict()

        # Define the joy sadness counts
        self.__joy_count = 0
        self.__active_count = 0
        self.__passive_count = 0
        self.__sadness_count = 0
        self.__total_layer_count = 0

        # Define the subsection emotional density list
        self.__emotion_densities = []

        # Loop through each layer and update the needed counts
        run_on_each_layer(image, None, None, self.__process_layer)

        # Calculate the active and passive measures and activity score
        self.__active_density = self.__active_count/self.__total_layer_count
        self.__passive_density = self.__passive_count/self.__total_layer_count
        self.__activity_score = abs(self.__active_density - self.__passive_density)

        # Calculate the minimum and maximum emotional densities
        for i in range(len(self.__emotion_densities)):
            emotional_density_info = self.__emotion_densities[i]
            self.__emotion_densities[i] = emotional_density_info["non_base_count"]/emotional_density_info["total_count"]
        self.__min_emotional_density = min(self.__emotion_densities)
        self.__max_emotional_density = max(self.__emotion_densities)

        # Calculate the note size interval from emotional densities
        num_potential_notes = 4
        ed_min_max_diff = abs(self.__max_emotional_density - self.__min_emotional_density)
        self.__ed_interval_size = ed_min_max_diff / num_potential_notes

        # Get the musical key of the song
        # Positive majority pictures are major
        # Negative majority pictures are minor
        if self.__positive_count > self.__negative_count:
            self.key = MUSIC_KEY_MAJOR
        else:
            self.key = MUSIC_KEY_MINOR

        # Get the top two emotions in the image
        # Not including the base emotion
        self.__secondary_emotion = None
        self.__tertiary_emotion = None
        # Remove the potential for base emotion being max
        # Store max as secondary emotion max
        self.__emotion_count[self.__base_emotion] = -1 
        self.__secondary_emotion = self.__get_dict_max_key(self.__emotion_count)
        # Remove the potential for secondary emotion being max
        # Store max as tertiary emotion max
        self.__emotion_count[self.__secondary_emotion] = -1
        self.__tertiary_emotion = self.__get_dict_max_key(self.__emotion_count)

        # Calculate main melody (melody_o) octave
        # Calculate the joy and sadness density
        # Plug abs of density diffs in to the mo octave equation
        joy_density = self.__joy_count/self.__total_layer_count
        sadness_density = self.__sadness_count/self.__total_layer_count
        js_density = abs(joy_density-sadness_density)

        self.mo_octave = (js_density-js_min)*(6-4)
        self.mo_octave = math.floor(self.mo_octave/(js_max-js_min))+4

        # Calculate the melody e1 octave
        self.me1_octave = self.__calculate_melody_octave(self.__secondary_emotion, self.mo_octave)
        # Calculate the melody e2 octave
        self.me2_octave = self.__calculate_melody_octave(self.__tertiary_emotion, self.mo_octave)

        # Calculate the melody
        self.melody = []
        num_sections = 4
        for i in range(len(self.__emotion_densities)):
            section = i // num_sections
            if section == len(self.melody):
                self.melody.append([])

            emotional_density = self.__emotion_densities[i]
            emotional_density -= self.__min_emotional_density
            if self.__ed_interval_size > 0:
                ed_bin = int(emotional_density // self.__ed_interval_size)
            else:
                ed_bin = 0

            global notes
            notes = list(melody_templates[ed_bin])
            if self.key == MUSIC_KEY_MAJOR:
                potential_pitches = list(c_major_pitch_consonance)
            else:
                potential_pitches = list(c_minor_pitch_consonance)

            # Split the subsection and calculate the emotional
            global num_notes
            num_notes = len(notes)
            layer_note_sections = []

            def split_layers_into_note_sections(layer):
                global num_notes
                global notes
                if layer["parent"]["index"]+(layer["parent"]["parent"]["index"]*4) == i:
                    layer_count = layer["max_index"]

                    if layer_count < num_notes:
                        diff = (num_notes - layer_count)*-2
                        notes = notes[:diff]
                        
                        num_notes = len(notes)

                    split_size = math.floor(layer_count / num_notes)
                    layer_bin = layer["index"] // split_size
                    
                    if layer_bin >= num_notes:
                        layer_bin = num_notes-1

                    base_emotion = layer["parent"]["emotion"]

                    if len(layer_note_sections) == layer_bin:
                        layer_note_sections.append({
                            "total_count": 0,
                            "non_base_count": 0
                        })

                    layer_note_sections[layer_bin]["total_count"] += 1
                    if layer["emotion"] != base_emotion:
                        layer_note_sections[layer_bin]["non_base_count"] += 1
            run_on_each_layer(image, None, None, split_layers_into_note_sections)
            
            for i in range(len(layer_note_sections)):
                sublayer = layer_note_sections[i]
                if sublayer["total_count"] != 0:
                    layer_note_sections[i] = sublayer["non_base_count"]/sublayer["total_count"]
                else:
                    layer_note_sections[i] = 0

            min_note_density = min(layer_note_sections)
            max_note_density = max(layer_note_sections)
            note_density_diff = max_note_density-min_note_density
            note_density_interval = note_density_diff / len(c_major_pitch_consonance)

            for i in range(len(layer_note_sections)):
                note_density = layer_note_sections[i]
                if note_density_interval == 0:
                    index = 0
                else:
                    index = int((note_density-min_note_density) // note_density_interval)
                    if index >= len(potential_pitches):
                        index = len(potential_pitches)-1
                pitch = potential_pitches[index]
                notes[i] = {
                    "note": notes[i],
                    "pitch": pitch
                }
            self.melody[section].append(notes)

        final_melody = []
        for section in self.melody:
            final_melody.append(section)
            final_melody.append(section)
        self.melody = final_melody

        # Calculate the tempo
        self.tempo = (self.__activity_score - act_min) * (180 - 40)
        self.tempo = self.tempo / (act_max - act_min)
        self.tempo = int(40 + self.tempo)

    def get_song_structure(self):
        return {
            "image": {
                "image_id": self.__image_details["image_id"],
                "image_url": self.__image_details["image_url"]
            },
            "key": self.key,
            "mo_octave": self.mo_octave,
            "me1_octave": self.me1_octave,
            "me2_octave": self.me2_octave,
            "tempo": self.tempo,
            "melody": self.melody
        }
    
    def __get_dict_max_key(self, dictionary):
        return max(dictionary.items(), key=operator.itemgetter(1))[0]

    def __calculate_melody_octave(self, emotion, initial_octave):
        # Return the relative octave of a melody compared to the initial octave
        octave_add = ["joy", "trust"]
        octave_subtract = ["anger", "fear", "sadness", "disgust"]
        if emotion in octave_add:
            return initial_octave+1
        elif emotion in octave_subtract:
            return initial_octave-1
        return initial_octave

    def __process_layer(self, layer):
        emotion = layer["emotion"]
        num_subsections = 4
        parent_subsection_index = layer["parent"]["index"]+(num_subsections*layer["parent"]["parent"]["index"])
        section_emotion = layer["parent"]["parent"]["emotion"]
        
        if len(self.__emotion_densities) == parent_subsection_index:
            self.__emotion_densities.append({
                "non_base_count": 0,
                "total_count": 0
            })

        # Check for joy sadness and add to counts
        self.__total_layer_count += 1
        if emotion == "joy":
            self.__joy_count += 1
        elif emotion == "sadness":
            self.__sadness_count += 1

        if emotion == "joy" or emotion == "anger":
            self.__active_count += 1
        elif emotion == "sadness":
            self.__passive_count += 1

        # Add to emotional count
        self.__emotion_count[emotion] = self.__emotion_count.get(emotion, 0)+1

        # Store the positive negative count
        if emotion in self.__positive_emotions:
            self.__positive_count += 1
        elif emotion in self.__negative_emotions:
            self.__negative_count += 1

        # Determine emotional density impact
        self.__emotion_densities[parent_subsection_index]["total_count"] += 1
        if emotion != section_emotion:
            self.__emotion_densities[parent_subsection_index]["non_base_count"] += 1
    
    