# import json
# from SPARQLWrapper import SPARQLWrapper, JSON
# from urllib.parse import urlparse

# def is_url(value):
#     if "http" in value:
#         return True
#     return False
    
# def fetch_label(entity):
#     # If entity contains 'nodeID' or is not a valid URL, return entity as is
#     if 'nodeID' in entity or not is_url(entity):
#         return entity
#     elif is_url(entity):

#         sparql = SPARQLWrapper("https://dblp-kg.ltdemos.informatik.uni-hamburg.de/sparql")
        
#         query = f"""
#             PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#             PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#             SELECT (?x0 AS ?value) WHERE {{
#                 SELECT DISTINCT ?x0 WHERE {{
#                     <{entity}> rdfs:label ?x0 .
#                 }}
#             }}
#         """
        
#         sparql.setQuery(query)
#         sparql.setReturnFormat(JSON)
#         results = sparql.query().convert()
#         labels = [result['value']['value'] for result in results['results']['bindings']]
#         return labels[0] if labels else entity


# def fetch_one_hop_relations(entity):
#     sparql = SPARQLWrapper("https://dblp-kg.ltdemos.informatik.uni-hamburg.de/sparql")
    
#     # Relations where entity is the subject
#     query1 = f"""
#         SELECT ?p ?o WHERE {{
#             <{entity}> ?p ?o .
#         }}
#     """
    
#     # Relations where entity is the object
#     query2 = f"""
#         SELECT ?s ?p WHERE {{
#             ?s ?p <{entity}> .
#         }}
#     """
    
#     relations = []
    
#     for query in [query1, query2]:
#         sparql.setQuery(query)
#         sparql.setReturnFormat(JSON)
#         results = sparql.query().convert()
#         for result in results['results']['bindings']:
#             s = result.get('s', {}).get('value', None)
#             p = result.get('p', {}).get('value', None)
#             o = result.get('o', {}).get('value', None)
#             relations.append((s, p, o))
            
#     return relations

# def main():
#     entity = "https://dblp.org/pid/95/2265"
#     question = "Show the Wikidata ID of the person Robert Schober." 
    
#     relations = fetch_one_hop_relations(entity)
    
#     labeled_pairs = []
#     for relation in relations:
#         s_label, p_label, o_label = None, None, None
        
#         if relation[0]:
#             s_label = fetch_label(relation[0])
#         if relation[1]:
#             p_label = fetch_label(relation[1])
#         if relation[2]:
#             o_label = fetch_label(relation[2])
            
#         labeled_pairs.append({
#             's': s_label,
#            # 's_Rel':relation[0],
#             'p': p_label,
#             #'p_Rel':relation[1],
#             'o': o_label,
#             #'o_Rel':relation[2],
#         })
    
#     output_data = {
#         'question': question,
#         'labeled_pairs': labeled_pairs
#     }
    
#     with open('labeled_pairs.json', 'w') as json_file:
#         json.dump(output_data, json_file, indent=4)

# if __name__ == "__main__":
#     main()
    

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
                <{entity}> ?p ?o .
                OPTIONAL {{ <{entity}> rdfs:label ?sLabel . }}
                OPTIONAL {{ ?p rdfs:label ?pLabel . }}
                OPTIONAL {{ ?o rdfs:label ?oLabel . }}
            }}
            UNION
            {{
                ?s ?p <{entity}> .
                OPTIONAL {{ <{entity}> rdfs:label ?oLabel . }}
                OPTIONAL {{ ?s rdfs:label ?sLabel . }}
                OPTIONAL {{ ?p rdfs:label ?pLabel . }}
            }}
        }}
    """
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
    # Condition 1
    # Condition 2
    # print(question.lower())
    if "wikidata" in question.lower():
        print("wikidata")
        if not ("wikidata" in pair['s'].lower() or "wikidata" in pair['o'].lower()):
            return False
        else:
            return True
    clean_question = re.sub(r"'[^']*'", "", question).lower()

    # Check condition
    if (("author" in clean_question or "wr" in clean_question) and ("publi" in clean_question or "paper" in clean_question)):
        print("author")
        if "autho" not in pair['p'].lower():
            return False
        else:
            return True
    if ("authored by" in clean_question):
        print("author")
        if "autho" not in pair['p'].lower():
            return False
        else:
            return True
    

    if "bibtex" in question.lower():
        print("hi")
        if not ("bibtex" in pair['p']):
            return False
        else:
            return True


    # Condition 3
    if "affiliat" in question:
        # print("primary")

        if not ("primary affiliation" in pair['p']):
            return False
        else:
            return True



    if "orcid" in question.lower():
        if not ("orcid" in pair['p']):
            return False
        else:
            return True
    if ("when" in question.lower()) or ("year" in question.lower()):
        if not ("year of publication" in pair['p']):
            return False
        else:
            return True

    if ("venue" in question.lower()) or ("where" in question.lower()):
        if not ("published in" == pair['p']):
            print("hi")
            return False
        else:
            return True
    if "webpage" in question.lower():
        # print("web page")

        if "web page URL" in pair['p']:
            return True
        else:
            return False
    if "http://www.w3.org/1999/02/22-rdf-syntax" in pair['p']:
        # print("syntax")
        return False

    # Condition 5
    if "nodeID" in pair['s'] or "nodeID" in pair['o']:
        # print("nodeID")
        return False

    return True

def main():
    entity = "https://dblp.org/rec/journals/midm/AndrewsCLGMH21"
    question = "Mention the venue in which 'The impact of data from remote measurement technology on the clinical practice of healthcare professionals in depression, epilepsy and multiple sclerosis: survey' was published." 
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
    
    output_data = {
        'question': question,
        'labeled_pairs': labeled_pairs
    }
    with open('labeled_pairs.json', 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

if __name__ == "__main__":
    main()
