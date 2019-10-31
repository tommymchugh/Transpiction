import json
class Emotion:
    def __init__(self, wiki_art_emotion):
        # Get the wikiart emotions conversion object
        emotions_conversion_file_name = "../../support/datasets/wikiart/generate_emotions/wiki_art_emotions_conversion.json"
        emotions_conversion_file_input = open(emotions_conversion_file_name, "r")
        emotions_conversion_text = emotions_conversion_file_input.read()
        emotions_conversion_file_input.close()

        emotions_conversion = json.loads(emotions_conversion_text)
        self.raw = wiki_art_emotion
        self.emotion = emotions_conversion[wiki_art_emotion]

    def get_raw_emotion(self):
        return self.raw
    
    def get_converted_emotion(self):
        return self.emotion