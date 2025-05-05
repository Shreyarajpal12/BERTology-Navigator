# Bertology Navigator

Submission of my KGQA system to SCHOLARLY QALD @ISWC 2023 
### README: KGQA on DBLP-QUAD for SCHOLARLY QALD at ISWC

---

#### Introduction

KGQA (Knowledge Graph Question Answering) on DBLP-QUAD is a project developed for the task of question answering over the DBLP Knowledge Graph, utilizing the DBLP-QUAD dataset. The task forms a part of the SCHOLARLY QALD challenge at ISWC, hosted on [Codalab Competition Page](https://codalab.lisn.upsaclay.fr/competitions/14264). The objective involves harnessing the power of machine learning, natural language processing, and knowledge graph exploration to retrieve accurate and concise answers to natural language questions. 

#### Task Details

**Task 1: DBLP-QUAD — Knowledge Graph Question Answering over DBLP**

- **Dataset**: DBLP-QUAD
- **Volume**: Consists of 10,000 question-SPARQL pairs.
- **Aim**: The task requires participants to develop systems to effectively answer natural language questions using the DBLP Knowledge Graph.

#### Our Approach

##### Phase 1: Relation Extraction
1. **One-Hop Relations**: Our system begins by extracting one-hop relations between entities.
2. **Labeled Candidate Pairs**: For every entity encountered, the system retrieves labeled candidate pairs from the DBLP Knowledge Graph.

##### Phase 2: Relation Selection
- **BERT cls Embeddings**: The system employs BERT cls embeddings to facilitate the selection of the most plausible relation between candidate pairs.
- **Winning Candidate Selection**: Based on the identified relations, the system chooses the winning candidate that would most likely yield the accurate answer.

#### Implementation and Testing

##### Test 1: Preliminary Testing
- **Dataset**: 200 questions extracted from DBLP QUAD’s original 2,000 question test set, specifically focusing on questions involving one-hop relations.
- **Result**: Achieved 100% accuracy.
- **Location**: Results can be accessed in `TEST_DBLP_DATASET/results`.

##### Test 2: Competition Test Set
- **Dataset**: Applied on the provided 500 test questions in the competition.
- **Location**: Results are available in the `500_questiondataset` folder.

#### Results and Findings

Detailed results, along with relevant graphs, charts, and discussion, are elaborated in the respective result folders. The high accuracy in the preliminary test set illustrates the system's competence in handling one-hop relations within the KG.
#### Repository Structure

```
KGQA-DBLP-QUAD/
│
├── Test_DBLP_DATASET/
│   ├── dataset/ - contains dataset with 200 questions selected from DBLP QUAD test dataset
│   └── results/ - contains labeled pairs and final accuracy results with winning candidates
│   ├── bertdataset.py -
│   └── st3dataset.py - 
│
├── 500_questiondataset/
│   ├── entity linked dataset/ - Entity linking and listing performed on 500 questions test dataset
│   └── results/ - contains labeled pairs and final accuracy results with winning candidates
│   ├── bert500ds.py -
│   └── st3500dat.py - 
├── Single_Question/
│   ├── accuracy_results.json - sample accuracy results with winning candidate for one question
│   └── labeled_pairs.json - contains labeled pairs for sample question
│   ├── bertimplement.py -
│   └── st3.py - 
│
├── requirements.txt
└── README.md
```

#### Dependencies and Setup

Ensure that you have Python 3.x installed. Install the necessary libraries and dependencies using the following command:

```bash
pip install -r requirements.txt
```

#### Usage

Provide instructions for how to run your code, query the model, or fine-tune it with additional data.

#### Contribution and Collaboration

We invite researchers and developers to contribute to the enhancement of KGQA on DBLP-QUAD. Feel free to raise issues, suggest enhancements, or create pull requests.

#### Citation and Acknowledgments

Ensure to provide due credits to datasets, models, and resources utilized during the project. Express gratitude towards contributors and collaborators.

#### License

Specify the license under which the project is being distributed.

---

