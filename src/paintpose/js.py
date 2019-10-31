from utils import run_on_each_layer

class JoySadnessDiffs:
    def __init__(self, emotion_map):
        joy_sadness_diffs = []
        activity_scores = []
        for i in range(len(emotion_map)):
            image = emotion_map[i]
            if image["emotion"] != "other":
                self.__joy_count = 0
                self.__sadness_count = 0

                self.__active_count = 0
                self.__passive_count = 0

                self.__total_count = 0

                run_on_each_layer(image, None, None, self.__process_layer)
                joy_density = self.__joy_count/self.__total_count
                sadness_density = self.__sadness_count/self.__total_count

                active_density = self.__active_count/self.__total_count
                passive_density = self.__passive_count/self.__total_count
                activity_score = abs(active_density - passive_density)
                activity_scores.append(activity_score)

                joy_sadness_diffs.append(abs(joy_density - sadness_density))
        self.js_min = min(joy_sadness_diffs)
        self.js_max = max(joy_sadness_diffs)
        self.act_max = max(activity_scores)
        self.act_min = min(activity_scores)
    
    def __process_layer(self, layer):
        emotion = layer["emotion"]
        index = layer["index"]
        self.__total_count += 1
        if emotion == "joy":
            self.__joy_count += 1
        elif emotion == "sadness":
            self.__sadness_count += 1

        if emotion == "joy" or emotion == "anger":
            self.__active_count += 1
        elif emotion == "sadness":
            self.__passive_count += 1

