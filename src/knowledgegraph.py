import networkx as nx
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from tqdm import tqdm
from typing import List, Tuple, Dict
import numpy as np

import nltk

try:
    from nltk.corpus import wordnet as wn
except LookupError:
    print("WordNet not found. Downloading...")
    nltk.download('wordnet')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class Concepts(BaseModel):
    concepts_list: List[str] = Field(description="List of concepts")

class knowledgeGraph:
    def __init__(self, openai_model):
        """
        Initializes the knowledgeGraph with a graph, lemmatizer and an NLP model.
        Attributes:
        - graph: An instance of networkx Graph.
        - lemmatizer: An instance of WordNetLemmatizer.
        - concept_cache: A dictionary to cache extracted concepts.
        - nlp: An instance of a spacy NLP model.
        - edges_threshold: A float value that sets the threshold for adding edges based on similartiy.
        """
        self.OpenAIModel = openai_model
        self.graph = nx.Graph()
        self.lemmatizer = WordNetLemmatizer()
        self.concept_cache = {}
        # self.nlp = self._load_transformers_model()
        # self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        self.edges_threshold = 0.8
    
    
    def build_graph(self, splits):
        """
        Builds the knowledge graph by adding nodes, creating embeddings, extract concepts, and adding edges.

        Args:
        - splits (list): A list of document splits.
        - llm: An instance of a large language model.
        - embeddings_model: An instance of an embedding model.

        Returns: 
        - None
        """
        self._add_nodes(splits)
        
        embeddings = self._create_embeddings(splits, self.OpenAIModel)
        self._extract_concepts(splits)   
        self._add_edges(embeddings)

    def _add_nodes(self, splits):
        """
        Adds nodes to the graph from the document splits.

        Args:
        - splits (list): A list of document splits.

        Returns:
        - None
        """
        
        for i, split in enumerate(splits):

            self.graph.add_node(i, content=split.page_content)


    def _create_embeddings(self,splits, openai_model):
        """
     f.   Creates embeddings for the document splits using embedding model.

        Args:
        - splits (list): A list of document splits.
        - embedding_model: An instance of an embedding model.

        Returns:
        - numpy.ndarray: An array of embeddings for the document splits.
        """
        embeddings = []
        for split in splits:
            embedd = self.OpenAIModel.embed_documents(split.page_content)
            embeddings.extend(embedd)
        embeddings = np.array(embeddings, dtype="float32")
        
        if embeddings.ndim ==1:
            embeddings = embeddings.reshape(1,-1)
        return embeddings
    
    def _compute_similarities(self, embeddings):
        """
        Computes the cosine similaritiy matrix for the embeddings.

        Args:
        - embeddings (numpy.ndarray): An array of embeddings.

        Returns:
        - numpy.ndarray: A cosine similarity matrix for embeddings.
        """
        
        similarity_matrix = cosine_similarity(embeddings)
       
        return similarity_matrix
    
    def named_entities(self, content):
        """
        Loads the spaCy NLP model, downloading it if necessary.

        Args:
        - None

        Returns:
        - spacy.Language: An instance of a spaCy NLP model.
        """
        prompt = [
            {"role": "system", 
             "content": f"Given the content:{content}, Extract Named entities from the content."
            }
        ]
        
        response = self.OpenAIModel.completion(prompt=prompt)
        named_entities = response.choices[0].message.content
        return named_entities
        # try:
        #     return spacy.load("en_core_web_sm")
        # except OSError:
        #     print("Downloading spaCy model....")
        #     download("en_core_web_sm")
        #     return spacy.load("en_core_web_sm")
    
  
    
    def _extra_concepts_and_entities(self, content):
        """
        Extracts concepts and named entities form the content using spaCy and LLM.
        Args: 
        - content (str): The content from which to extract concepts and entities.
        - llm: An instance of large language model.

        Returns:
        - list: A list of extracted concepts and entities.
        """
        
        if content in self.concept_cache:
            return self.concept_cache[content]
        
        named_entities = [self.named_entities(content)]

        
        # doc = self.nlp(content)
        # named_entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "WORK_OF_ART"]]
        prompts = (
            f"Extract key concepts (excluding named entities) from the following text:\n\n"
            f"{content}\n\n"
            f"Key concepts:"
        )
        response = self.OpenAIModel.completion(prompt=[{"role": "user", "content": prompts}],
                                                  temperature=0.4)
        general_concepts = response.choices[0].message.content.strip().split(', ')

        all_concepts = list(set(named_entities + general_concepts))

        self.concept_cache[content] = all_concepts
        return all_concepts
    
    def _extract_concepts(self, splits ):
        """
        Extracts concepts for all documents splits using multi-threading.

        Args:
        - splits (list): A list of document splits.
        - llm: An instance of large language model.

        Returns:
        - None
        """
        with ThreadPoolExecutor() as executor:
            future_to_node = {executor.submit(self._extra_concepts_and_entities, split.page_content):i
                            for i , split in enumerate(splits)}
            
            for future in tqdm(as_completed(future_to_node), total= len(splits), desc= "Extracting concepts and entitites"):
                node = future_to_node[future]
                concepts = future.result()
                self.graph.nodes[node]['concepts'] = concepts 

    def _add_edges(self, embeddings):
        """
        Adds edges to the graph based on th similarity of embeddings and shared concepts.
        
        Args:
        - embeddings (numpy.ndarray): An array of embeddings for the document splits.
        Returns:
        -None
        """  
        similarity_matrix = self._compute_similarities(embeddings)
        
        num_nodes = len(self.graph.nodes)
        
        for node1 in tqdm(range(num_nodes), desc="Adding edges"):
            for node2 in range(node1 + 1, num_nodes):
                try:
                    similarity_score = similarity_matrix[node1][node2]
                except IndexError as e:
                    print(f"IndexError for node1: {node1}, node2: {node2} - {e}")
                    continue

                if similarity_score>self.edges_threshold:
                    shared_concepts = set(self.graph.nodes[node1]['concepts']) & set(self.graph.nodes[node2]['concepts'])
                    edge_weight = self._calculate_edge_weight(node1, node2, similarity_score, shared_concepts) 
                    self.graph.add_edge(node1, node2, weight = edge_weight,
                                        similarity= similarity_score,
                                        shared_concepts = list(shared_concepts))


    def _calculate_edge_weight(self, node1, node2, similarity_score, shared_concepts, alpha=0.7, beta=0.3):
        """
        Calculate the weight of an edge based on similarity score and shared concepts.

        Args:
        - node1 (int): The first node.
        - node2 (int): The second node.
        - similarity_score (float): The similarity score between the nodes.
        - shared_concepts (set): The set of shared concepts between the nodes.
        - alpha (float, optional): The weight of the similarity score. Default is 0.7.
        - beta (float, optional): The weight of the shared concepts. Default is 0.3.

        Returns:
        - float: The calculated weight of the edge.
        """ 
        max_possible_shared = min(len(self.graph.nodes[node1]['concepts']), len(self.graph.nodes[node2]['concepts']))
        normalized_shared_concepts = len(shared_concepts)/ max_possible_shared if max_possible_shared > 0 else 0
        return alpha*similarity_score*beta*normalized_shared_concepts
    
    def _lemmatize_concepts(self, concept):
        """
        Lemmatizes a given concept.

        Args:
        - str: The lemmatized concepts.
        """
        
        return ' '.join([self.lemmatizer.lemmatize(word) for word in concept.lower().split()])