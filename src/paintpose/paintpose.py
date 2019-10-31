import json
import math
from midiutil.MidiFile import MIDIFile
from emotion import Emotion
from image import Image
from js import JoySadnessDiffs

# Open the wikiart emotion map
emotion_map_file_name = "image_emotion_maps.json"
emotion_map_file_path = "../../support/datasets/wikiart/generate_emotions/{}".format(emotion_map_file_name)

emotion_map_file_input = open(emotion_map_file_path, "r")
emotion_map_file_text = emotion_map_file_input.read()
emotion_map_file_input.close()
# Convert the wikiart map into a json object
emotion_map = json.loads(emotion_map_file_text)

# Get the emotional positive and negative categories
positive_emotions = []
negative_emotions = []
# Get color emotions file
color_emotions_file_name = "../../support/datasets/wikiart/generate_emotions/color_emotions.json"
color_emotions_file_input = open(color_emotions_file_name, "r")
color_emotions_text = color_emotions_file_input.read()
color_emotions_file_input.close()

color_emotions = json.loads(color_emotions_text)
# Check which emotion type the emotion is 
# save it to the proper category
for emotion in color_emotions:
    if emotion["type"] == "negative":
        negative_emotions.append(emotion["emotion"])
    elif emotion["type"] == "positive":
        positive_emotions.append(emotion["emotion"])

# Calculate joy sadness diff min and max
joy_sadness_diffs = JoySadnessDiffs(emotion_map)
js_min = joy_sadness_diffs.js_min
js_max = joy_sadness_diffs.js_max

# Calculate act max and min
act_max = joy_sadness_diffs.act_max
act_min = joy_sadness_diffs.act_min

# Get the total melodies of the images
songs = list()
for i in range(len(emotion_map)):
    image = emotion_map[i]
    if image["emotion"] != "other":
        processed_image = Image(image, positive_emotions, negative_emotions, act_max, act_min, js_max, js_min)
        songs.append(processed_image.get_song_structure())
    print(i)

# Save songs to disk
song_data_output_file_name = "songs.json"
song_data_output = open(song_data_output_file_name, "w")
song_data_output.write(json.dumps(songs))
song_data_output.close()

OUTPUT_MIDI = 0
OUTPUT_FREQUENCY = 1

output = OUTPUT_FREQUENCY

length_conversion = {
    0: 4.0,
    1: 2.0,
    2: 1.0,
    3: 0.5,
    4: 0.25
}

def get_midi_pitch(pitch, octave):
    return (12*(octave+1)) + pitch

if output == OUTPUT_MIDI:
    # Generate midi-files
    for i in range(len(songs)):
        print(i)
        song = songs[i]
        midi_file = MIDIFile(3)
        tracks = [0, 1, 2]
        time = 0

        midi_file.addTrackName(tracks[0], time, "Melody O")
        midi_file.addTrackName(tracks[1], time, "Melody E1")
        midi_file.addTrackName(tracks[2], time, "Melody E2")

        midi_file.addTempo(tracks[0], time, song["tempo"])
        midi_file.addTempo(tracks[1], time, song["tempo"])
        midi_file.addTempo(tracks[2], time, song["tempo"])

        channel = 0
        volume = 100

        track_one_octave = song["mo_octave"]
        track_two_octave = song["me1_octave"]
        track_three_octave = song["me2_octave"]

        existing_duration = 0.0
        for section in song["melody"]:
            for measure in section:
                for note in measure:
                    note_length = note["note"]
                    pitch = note["pitch"]

                    track_one_note = get_midi_pitch(pitch, track_one_octave)
                    track_two_note = get_midi_pitch(pitch, track_two_octave)
                    track_three_note = get_midi_pitch(pitch, track_three_octave)

                    note_duration = length_conversion[note_length]
                    note_time = existing_duration

                    midi_file.addNote(tracks[0], channel, track_one_note, note_time, note_duration, volume)
                    midi_file.addNote(tracks[1], channel, track_two_note, note_time, note_duration, volume)
                    midi_file.addNote(tracks[2], channel, track_three_note, note_time, note_duration, volume)
                    existing_duration += note_duration

        with open("midi_files/{}.mid".format(song["image"]["image_id"]), 'wb') as outf:
            midi_file.writeFile(outf)
elif output == OUTPUT_FREQUENCY:
    song_encoded_frequencies = []
    for song in songs:
        total_count = 0
        frequency_output = dict()

        for num in range(60):
            midi_pitch = 48+num
            frequency_output[midi_pitch] = {
                                    "count": 0,
                                    "pitches": 0
                                }

        track_one_octave = song["mo_octave"]
        track_two_octave = song["me1_octave"]
        track_three_octave = song["me2_octave"]

        for section in song["melody"]:
            for measure in section:
                for note in measure:
                    total_count += 3
                    note_length = note["note"]
                    pitch = note["pitch"]

                    track_one_note = get_midi_pitch(pitch, track_one_octave)
                    track_two_note = get_midi_pitch(pitch, track_two_octave)
                    track_three_note = get_midi_pitch(pitch, track_three_octave)
                    note_duration = length_conversion[note_length]

                    frequency_output_one = frequency_output[track_one_note]
                    frequency_output_one["count"] += 1
                    frequency_output_one["pitches"] += note_duration
                    frequency_output[track_one_note] = frequency_output_one

                    frequency_output_two = frequency_output[track_two_note]
                    frequency_output_two["count"] += 1
                    frequency_output_two["pitches"] += note_duration
                    frequency_output[track_two_note] = frequency_output_two

                    frequency_output_three = frequency_output[track_three_note]
                    frequency_output_three["count"] += 1
                    frequency_output_three["pitches"] += note_duration
                    frequency_output[track_three_note] = frequency_output_three
        
        encoded_pitches = []
        for pitch in frequency_output.keys():
            value = frequency_output[pitch]

            frequency = round(value["count"]/total_count, 4)
            if value["count"] == 0:
                average_length = 0
            else:
                average_length = round(value["pitches"]/value["count"], 4)
            encoded_pitches.append((float(pitch), 
                                    float(frequency), 
                                    float(average_length)))
        
        song_encoded_frequencies.append({
            "id": song["image"]["image_id"],
            "pitches": encoded_pitches
        })
    
    # write to output
    encoded_output_file_name = "encoded_songs.json"
    encoded_output = open(encoded_output_file_name, "w")
    encoded_output.write(json.dumps(song_encoded_frequencies))
    encoded_output.close()
        








