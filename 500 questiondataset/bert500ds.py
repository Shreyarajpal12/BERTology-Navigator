import json
import torch
import time
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

def process_data():
    # Load data
    with open('labeled_pairs_dataset.json', 'r') as f:
        data = json.load(f)

    all_results = []
    for idx, entry in enumerate(data):
        labeled_pairs = entry['labeled_pairs']
        question = entry['question']
        question_embedding = get_cls_embedding(question)
        highest_similarity = -1
        winning_candidate = None
        start_time = time.time()
        for pair in labeled_pairs:
            text = f"[CLS] {pair['s']} [SEP] {pair['p']} [SEP] {pair['o']}"
            candidate_embedding = get_cls_embedding(text)
            similarity = cosine_similarity(question_embedding, candidate_embedding, dim=0).item()
            if similarity > highest_similarity:
                highest_similarity = similarity
                winning_candidate = pair

        elapsed_time = time.time() - start_time
        if elapsed_time > 8 * 60:  # Check if processing time exceeds 8 minutes.
            print("Issue: Processing exceeded 8 minutes for question:", question)

        all_results.append({
            'question': question,
            'cosine_similarity': highest_similarity,
            'winning_candidate': winning_candidate
        })

        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1} questions...")

    with open('winning_candidates_results.json', 'w') as f:
        json.dump(all_results, f, indent=4)

if __name__ == "__main__":
    print("execution begin")
    process_data()
    print("execution complete")
