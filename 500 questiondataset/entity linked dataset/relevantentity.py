import json

def process_name(name):
    """Splits a name string into separate words based on spaces."""
    return name.split()

def count_common_words(label_words, entity_words):
    """Counts the number of common words between two word lists."""
    return len(set(label_words) & set(entity_words))

def extract_relevant_entity(data_entry):
    """Extracts the most relevant entity based on the label from the provided data entry."""
    label = data_entry["entities"]["entitylinkingresults"][0]["label"]
    results = data_entry["entities"]["entitylinkingresults"][0]["result"]

    label_words = process_name(label)
    
    # Find the entity with the most common words with the label
    max_common_count = 0
    most_relevant_url = None
    for score, (url, entity_label) in results:
        entity_words = process_name(entity_label)
        common_count = count_common_words(label_words, entity_words)
        if common_count > max_common_count:
            max_common_count = common_count
            most_relevant_url = url

    return most_relevant_url

if __name__ == "__main__":
    # Load the dataset
    with open('500entity.json', 'r') as f:
        dataset = json.load(f)

    # Extract the relevant entity for each entry
    for entry in dataset:
        entry["relevant_entity"] = extract_relevant_entity(entry)

    # Save the updated dataset to another file
    with open('outputentity.json', 'w') as f:
        json.dump(dataset, f, indent=4)

