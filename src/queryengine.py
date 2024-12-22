import numpy as np
from typing import List, Tuple, Dict
import heapq
from typing import List, Tuple, Dict

    
class AnswerCheck():
    def __init__(self, openai_model,model="gpt-4o-mini"):
        """
        Initializes the answer-checking mechanism with custom model.
        """
        self.model = model
        self.OpenAIModel = openai_model

    def check_answer(self, query, context):
        """
        Checks if the current context provides a complete answer to the query.

        Args:
        - query (str): The query to be answered.
        - content (str): The current context.

        Returns:
        - tuple: (is_complete (bool), answer (str))
        """
        prompt = [
            {"role": "system", 
             "content": f"Given the query {query} and the context:{context}, tell if the context provides a complete answer? Yes or No. If yes, provide the answer."
            }
        ]
        
        response = self.OpenAIModel.completion(prompt=prompt)
        text_response = response.choices[0].message.content.replace("Yes, the context provides a complete answer.", "")
        is_complete = "Yes" in text_response

        answer = text_response if is_complete else None
        return is_complete, answer

class QueryEngine:
    def __init__(self, vector_store, knowledge_graph,openai_model, documents, model_name = 'distilbert-base-uncased', model="gpt-4o-mini"):
        
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        
        self.documents = documents
        self.openai_model = openai_model
        self.answer_check = AnswerCheck(openai_model=self.openai_model)
        self.model = model
        self.openai_model = openai_model
        self.max_content_length = 4000

    def get_embedding(self, text):
        """
        Generates embeddings for the given text using OpenAI's embedding model.

        Args:
        - text (str): The text to embed.

        Returns:
        - np.ndarray: Embedding vector for the input text.
        """
        text = text.replace("\n", " ")

        embeddings = self.openai_model.embed_documents(text)
        return embeddings

    def generate_answer(self, query, context):
        """
        Generate a final answer to the query using OpenAI's completion API.

        Args:
        - query (str): The query to be answered.
        - context (str): The current context.

        Returns:
        - str: The final answer to the query.
        """

        prompt = [
            {"role": "system", 
             "content": f"Given the query {query} and the context: {context}, is the context provides the complete. If yes, provide the answer."
            }
        ]
        
        response = self.openai_model.completion(prompt=prompt)
        if "Yes" in response.choices[0].message.content:
            prompt = [
            {"role": "system", 
             "content": f"Given the query {query} and the context: {context},just Answer the query."
            }
        ]
            final_response = self.openai_model.completion(prompt=prompt, temperature =0.3)
            final_response = final_response.choices[0].message.content.replace("Yes, the context provides a complete answer.", "")
            
            return final_response
        return response.choices[0].message.content.replace("Yes, the context provides a complete answer.", "")
    
    def _expand_context(self, query: str, relevant_docs) -> Tuple[str, List[int], Dict[int, str], str]:
        """
        Expands the context by traversing the knowledge graph using a Dijkstra-like approach.

        This method implements a modified version of Dijkstra's algorithm to explore the knowledge graph.
        prioritizing the most relevant and strogly connected information. The algorithm works as follows:
        
        1. Initialize:
            - Start with nodes corresponding to the most relevant documents.
            - Use a priority queue to manage the traversal order, where priority is based on connection strength.
            - Maintain a dictionary of best known "distances" (invesrse of connection strengths) to each node.

        2. Traverse:
            - Always exploere the node with the highest priority (strogest connection) next.
            - For each node, check if we've found a complete answer.
            - Explore the nodes's neighbors, updating their priorities if a stronger connection is found.

        3. Concept Handling:
            - Track visited concepts to guide the exploration towards new, relevant information.
            - Expand to neighbors only if they introduce new concepts.

        4. Termination:
            - Stop if a complete answer is found.
            - Continure until the priority queue is empty (all reachable nodes explored).
        This approach ensures that:
        - We prioritize the most relevant and strogly connected information.
        - We explore new concepts systematically.
        - We find the most relevant answer by following the strongest connections in the knowledge graph.

        Args:
        - query (str): The query to be answered.
        - relevant_docs (List[Document]): A list of relevant documents to start the traversal.

        Returns:
        - tuple: A tuple containing:
            - expanded_context (str): The accumulated context from traversed nodes.
            - tranversal_path (List[int]): The sequence of node indices visited.
            - filtered_content (Dict[int, str]): A mapping of node indices to their content.
            - final_answer (str): The final answer found, if any.
        """
        expanded_context = ""
        traversal_path = []
        visited_concepts = set()
        filtered_content = {}
        final_answer = ""

        priority_queue = []
        distances = {}
        print("\nTraversing the knowledge graph:")

        for doc in relevant_docs:
            similarity_score,indices  = self.vector_store.search(self.get_embedding(doc.page_content), k=1)
            closest_node_content = [self.documents[i] for i  in indices[0]]
            closest_node = next(n for n in self.knowledge_graph.graph.nodes if self.knowledge_graph.graph.nodes[n]['content'] == closest_node_content[0].page_content)
            priority = 1/similarity_score
            heapq.heappush(priority_queue, (priority, closest_node))
            distances[closest_node]= priority
        step=0
        while priority_queue:
            current_priority, current_node = heapq.heappop(priority_queue)

            if current_priority> distances.get(current_node, float('inf')):
                continue

            if current_node not in traversal_path:
                step +=1
                traversal_path.append(current_node)
                node_content = self.knowledge_graph.graph.nodes[current_node]['content']
                node_concepts = self.knowledge_graph.graph.nodes[current_node]['concepts']

                filtered_content[current_node] = node_content
                expanded_context += "\n" + node_content if expanded_context else node_content
                print(""*50)
                # Check if we have a complete answer with the current context
                is_complete, answer  = self.answer_check.check_answer(query, expanded_context)
                if is_complete:
                    final_answer = answer
                    break
                node_concepts_set = set(self.knowledge_graph._lemmatize_concepts(c) for c in node_concepts)
                if not node_concepts_set.issubset(visited_concepts):
                    visited_concepts.update(node_concepts_set)
                    for neighbor in self.knowledge_graph.graph.neighbors(current_node):
                        edge_data = self.knowledge_graph.graph[current_node][neighbor]
                        edge_weight = edge_data['weight']

                        # Calcualte new distance (priority) to the neighbor
                        distance = current_priority + (1/edge_weight)

                        # If we've found a stronger connection to the neighor, update its distance
                        if distance < distances.get(neighbor, float('inf')):
                            distances[neighbor] = distance
                            heapq.heappush(priority_queue, (distance, neighbor))

                            if neighbor not in traversal_path:
                                step+=1
                                traversal_path.append(neighbor)
                                neighbor_content = self.knowledge_graph.graph.nodes[neighbor]['content']
                                neighbor_concepts = self.knowledge_graph.graph.nodes[neighbor]['concepts']

                                filtered_content[neighbor] = neighbor_content
                                expanded_context +="\n"+neighbor_content if expanded_context else neighbor_content

                                print(f"Concepts: {', '.join(neighbor_concepts)}")
                                print("-" * 50)

                                is_complete, answer = self.answer_check.check_answer(query, expanded_context)
                                if is_complete:
                                    final_answer = answer
                                    break
                                neighbor_concepts_set = set(self.knowledge_graph._lemmatize_concepts(c) for c in neighbor_concepts)
                                if not neighbor_concepts_set.issubset(visited_concepts):
                                    visited_concepts.update(neighbor_concepts_set)

                if final_answer:
                    break
        if not final_answer:
            print("\nGenerating final answer...")
            final_answer = self.generate_answer(query, expanded_context)
            final_answer.replace("Yes, the context provides a complete answer.", "")

        return expanded_context, traversal_path, filtered_content, final_answer

    def query(self, query: str) -> Tuple[str, List[int], Dict[int, str]]:
        """
        Processes a query by retrieving relevant docments, expanding the context, and generating the final answer.

        Args:
        - query (str): The query to be answered.

        Returns:
        - tuple: A tuple containing:
            - final_answer (str): The final answer to the query.
            - traversal_path (list): The traversal path of nodes in the knowledge graph.
            - filtered_content (dict): The filtered content of nodes.
        """
        #Retrieve relevant documents based on the query
        relevant_docs = self._retrieve_relevant_documents(query)
        #Expand the context using custom logic
        expanded_context, tranversal_path, filtered_content, final_answer = self._expand_context(query, relevant_docs)

        if not final_answer:

            prompt = [
            {"role": "system", 
             "content": f"Given the query and the context: {expanded_context},just Answer the query."
            },
            {
                "role": "user",
                "content": f"Here's my query: {query}"
            }
        ]
            response = self.openai_model.completion(prompt=prompt, temperature =0.3,max_tokens=500)
            final_answer = response.choices[0].message.content.repalce("Yes, the context provides a complete answer.", "")
            #Token usuage details
            total_tokens = response['usage']['total_tokens']
            prompt_tokens = response['usage']['prompt_tokens']
            completion_tokens = response['usage']['completion_tokens']

            cost_per_token = 0.000002
            total_cost = total_tokens * cost_per_token

            print(f"Total Tokens: {total_tokens}")
            print(f"Prompt Tokens: {prompt_tokens}")
            print(f"Completion Tokens: {completion_tokens}")
            print(f"Total Cost (USD): {total_cost:.8f}")

        return final_answer, tranversal_path, filtered_content
    
    
    def _retrieve_relevant_documents(self, query:str):
        """
        Retrieves relevant documents based on the query using the vector store.

        Args:
        - list: A list of relevant documents.
        """            
        print("\nRetrieving relevant documents....")
        #Perform FAISS-based document retrieval
        query_embedding = self.get_embedding(query)
        # np.array([query_embedding])
        distance, indices = self.vector_store.search(query_embedding, k=5)
        relevant_docs = [self.documents[i] for i in indices[0] ] #if i < len(self.documents)
        return relevant_docs

        

    

                        