import torch
import json
from transformers import BertTokenizer, BertModel
from torch.nn.functional import cosine_similarity
from SPARQLWrapper import SPARQLWrapper, JSON

MODEL_NAME = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)
def get_cls_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        return outputs.last_hidden_state[0, 0]
from SPARQLWrapper import SPARQLWrapper, JSON

def fetch_uri_from_label(label):
    """Fetch URI for a given label using SPARQL."""
    sparql = SPARQLWrapper("https://dblp-kg.ltdemos.informatik.uni-hamburg.de/sparql")
    query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?resource WHERE {{
            ?resource rdfs:label "{label}" .
        }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    if results['results']['bindings']:
        return results['results']['bindings'][0]['resource']['value']
    return None

# Test


# Load data
with open('labeled_pairs.json', 'r') as f:
    data = json.load(f)
    labeled_pairs = data['labeled_pairs']  # Assuming you want to process all candidates

question = data['question']
question_embedding = get_cls_embedding(question)

# Process in batches of 20
batch_size = 20
winning_candidate = None
highest_similarity = -1

# To store results for the output JSON file
results = []

for i in range(0, len(labeled_pairs), batch_size):
    batch = labeled_pairs[i:i+batch_size]
    batch_texts = [f"[CLS] {item['s']} [SEP] {item['p']} [SEP] {item['o']}" for item in batch]
    batch_embeddings = [get_cls_embedding(text) for text in batch_texts]
    
    # Compute cosine similarities
    similarities = [cosine_similarity(question_embedding, candidate_embedding, dim=0).item() for candidate_embedding in batch_embeddings]
    
    # Append results for the batch to the results list
    for j, text in enumerate(batch_texts):
        results.append({
            'text': text,
            'embedding': batch_embeddings[j].tolist(),  # Convert tensor to list
            'similarity': similarities[j]
        })
    # Find highest similarity in this batch
    max_similarity = max(similarities)
    if max_similarity > highest_similarity:
        highest_similarity = max_similarity
        winning_candidate = batch[similarities.index(max_similarity)]


def compare_with_gold(question_str, winning_candidate_value):
    with open('improveddataset.json', 'r') as f:
        dataset = json.load(f)
    print(question_str)
    gold_answers = []
    for entry in dataset['questions']:
        # print(entry)
        if entry['paraphrased_question']['string'] == question_str:
            print("yes baby")
        if entry['question']['string'] == question_str or (entry.get('paraphrased_question') and entry['paraphrased_question']['string'] == question_str):
            print("hi")

            for binding in entry['answer']['results']['bindings']:
                if binding['answer']['type']:
                    gold_answers.append(binding['answer']['value'])
            print(gold_answers)
            break

    # Check if none of the 's', 'p', 'o' contain 'http' and all gold answers don't contain 'http'
    if all("http" not in winning_candidate[key] for key in ['s', 'p', 'o']) and all("http" in answer for answer in gold_answers):
        print("i am in baby ", all("http" not in winning_candidate[key] for key in ['s', 'p', 'o']) and all("http" not in answer for answer in gold_answers))
        o_uri = fetch_uri_from_label(winning_candidate['o'])
        s_uri = fetch_uri_from_label(winning_candidate['s'])
        if o_uri:
            winning_candidate['o'] = o_uri
        if s_uri:
            winning_candidate['s'] = s_uri

    accuracy = (1 if (winning_candidate['o']) in gold_answers else 0)  or (1 if (winning_candidate['s']) in gold_answers else 0)  # 1 for correct, 0 for incorrect

    return gold_answers, accuracy

# Assuming you have 'question' and 'winning_candidate' defined elsewhere in the code
gold_answer, accuracy = compare_with_gold(question, winning_candidate)
output_data = {
    'gold_answer': gold_answer,
    #assuming this to be in a dataset where gold_Answer is available if not then function that finds accuracy(compare_with_gold) will be changed
    'accuracy': accuracy,
    'cosine_similarity': highest_similarity,
    'winning_candidate': winning_candidate
}

with open('accuracy_results.json', 'w') as f:
    json.dump(output_data, f, indent=4)
print("Winning Candidate:", winning_candidate)
