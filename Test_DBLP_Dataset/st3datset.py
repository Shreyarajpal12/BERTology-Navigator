import json, re
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import urlparse

def is_url(value):
    return "http" in value

def fetch_one_hop_relations_and_labels(entity):
    sparql = SPARQLWrapper("https://dblp-kg.ltdemos.informatik.uni-hamburg.de/sparql")
    query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?s ?p ?o ?sLabel ?pLabel ?oLabel WHERE {{
            {{
                {entity} ?p ?o .
                OPTIONAL {{ {entity} rdfs:label ?sLabel . }}
                OPTIONAL {{ ?p rdfs:label ?pLabel . }}
                OPTIONAL {{ ?o rdfs:label ?oLabel . }}
            }}
            UNION
            {{
                ?s ?p {entity} .
                OPTIONAL {{ {entity} rdfs:label ?oLabel . }}
                OPTIONAL {{ ?s rdfs:label ?sLabel . }}
                OPTIONAL {{ ?p rdfs:label ?pLabel . }}
            }}
        }}
    """
    # if '<' not in entity:
    #    entity= '<'+entity
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    relations = []
    for result in results['results']['bindings']:
        s = result.get('s', {}).get('value', entity)
        p = result.get('p', {}).get('value', None)
        o = result.get('o', {}).get('value', entity)
        s_label = result.get('sLabel', {}).get('value', s)
        p_label = result.get('pLabel', {}).get('value', p)
        o_label = result.get('oLabel', {}).get('value', o)
        relations.append(((s, s_label), (p, p_label), (o, o_label)))
        # print(relations)
    return relations

def valid_pair(pair, question):
    clean_question = re.sub(r"'[^']*'", "", question).lower()
    # Condition 1
    if "wikidata" in clean_question:
        if not ("wikidata" in pair['s'].lower() or "wikidata" in pair['o'].lower()):
            return False
        else:
            return True
    # Condition 2
    if (("author" in clean_question or "wr" in clean_question) and ("publi" in clean_question or "paper" in clean_question)):
        if "autho" not in pair['p'].lower():
            return False
        else:
            return True
    # Condition 3
    if ("authored by" in clean_question):
        if "autho" not in pair['p'].lower():
            return False
        else:
            return True
    # Condition 4
    if "bibtex" in clean_question:
        if not ("bibtex" in pair['p']):
            return False
        else:
            return True
    # Condition 5
    if "affiliat" in clean_question:
        if not ("primary affiliation" in pair['p']):
            return False
        else:
            return True
    # Condition 6
    if "orcid" in clean_question:
        if not ("orcid" in pair['p']):
            return False
        else:
            return True
    # Condition 7
    if ("when" in clean_question) or ("year" in clean_question):
        if not ("year of publication" in pair['p']):
            return False
        else:
            return True
    # Condition 8
    if ("venue" in clean_question) or ("where" in clean_question):
        if not ("published in" == pair['p']):
            return False
        else:
            return True
    # Condition 9
    if "webpage" in clean_question:
        if "web page URL" in pair['p']:
            return True
        else:
            return False
    if "http://www.w3.org/1999/02/22-rdf-syntax" in pair['p']:
        return False

    # Condition 10
    if "nodeID" in pair['s'] or "nodeID" in pair['o']:
        return False
    return True

def process_dataset(dataset):
    output = []

    for record in dataset['questions']:
        question = record["question"]["string"]
        entity = record["entities"][0]  # assuming there's only one entity per record

        relations = fetch_one_hop_relations_and_labels(entity)
        labeled_pairs = []
        
        for relation in relations:
            s, p, o = relation[0][0], relation[1][0], relation[2][0]
            s_label, p_label, o_label = relation[0][1], relation[1][1], relation[2][1]
            
            pair = {
                's': s_label,
                'p': p_label,
                'o': o_label,
            }

            if valid_pair(pair, question):
                labeled_pairs.append(pair)

        record_output = {
            'id': record["id"],
            'question': question,
            'labeled_pairs': labeled_pairs
        }

        output.append(record_output)

    return output

def main():
    # Load the dataset from 'improveddataset.json'
    with open('improveddataset.json', 'r') as json_file:
        dataset = json.load(json_file)

    output_data = process_dataset(dataset)

    with open('all_labeled_pairs.json', 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

if __name__ == "__main__":
    print("extraction begin")
    main()
    print("extraction complete")


