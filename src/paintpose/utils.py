def run_on_each_layer_for_map(emotion_map, section_action=None, subsection_action=None, layer_action=None):
    for image in emotion_map:
        run_on_each_layer(image, section_action, subsection_action, layer_action)

def run_on_each_layer(image, section_action=None, subsection_action=None, layer_action=None):
    # Loop through each layer and update the needed counts
    sections = image["sections"]
    for section_index in range(len(sections)):
        # Run the section action
        section = sections[section_index]
        section_info = {
            "emotion": section["section"], 
            "index": section_index,
            "max_index": len(sections)
        }
        if section_action != None:
            section_action(section_info)

        # Get all subsection
        subsections = section["subsections"]
        for subsection_index in range(len(subsections)):
            # Run the subsection action
            subsection = subsections[subsection_index]
            subsection_info = {
                "emotion": subsection["subsection"],
                "index": subsection_index,
                "parent": section_info,
                "max_index": len(subsections)
            }
            if subsection_action != None:
                subsection_action(subsection_info)

            # Get all the layers
            layers = subsection["layers"]
            for layer_index in range(len(layers)):
                # Run the layer action
                layer = layers[layer_index]
                if layer_action != None:
                    layer_action({
                        "emotion": layer,
                        "index": layer_index,
                        "parent": subsection_info,
                        "max_index": len(layers)
                    })
