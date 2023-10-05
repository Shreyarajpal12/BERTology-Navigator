import requests
import json

def get_entities(question, label_generator="t5-small", embedding_reranker="distmult"):
    base_url = "https://ltdemos.informatik.uni-hamburg.de/dblplinkapi/api/entitylinker"
    endpoint_url = f"{base_url}/{label_generator}/{embedding_reranker}"
    payload = {"question": question}
    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def process_dataset(dataset):
    results = []
    for item in dataset:
        question = item["question"]
        entities = get_entities(question)
        if entities:
            result = {
                "id": item["id"],
                "question": question,
                "entities": entities
            }
            results.append(result)
        else:
            print(f"Failed to fetch entities for {item['id']}.")
    return results

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    dataset = load_from_file("500qdblp.json")
    processed_data = process_dataset(dataset)
    save_to_file(processed_data, "500entity.json")
