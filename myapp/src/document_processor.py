from langchain_text_splitters import RecursiveCharacterTextSplitter
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import os 
from dotenv import load_dotenv

# from google.cloud import secretmanager

# client = secretmanager.SecretManagerServiceClient()
# project_id = "chrome-encoder-426804-u1"
# secret_id = "API_KEY"
# version_id = "1"
# name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
# response = client.access_secret_version(request={"name": name})
# api_key = response.payload.data.decode("UTF-8")

class OpenAIEmbedding:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
            
    def embed_documents(self, documents, model = "text-embedding-3-small", batch_size = 32):
        """
        Generate embeddings for a list of documents using OpenAI API.
        Args:
        
        Returns:
        - np.array: A 2D Numpy array where each row is the embedding for a document. 
        """
        documents = documents.replace("\n", " ")
        response = self.client.embeddings.create(
                input=[documents],
                model= model
            )
        embeddings = [data.embedding for data in response.data]
            
        return np.array(embeddings)
    
    def completion(self, prompt, model="gpt-4o-mini", max_tokens=150, temperature = 0.3):
        
        response = self.client.chat.completions.create(
            n=1,
            model= model,
            messages= prompt,
            max_tokens=max_tokens,
            temperature=temperature)
        
        return  response

class DocumentProcessor:
    def __init__(self, model="text-embedding-3-small"):
        """
        Initializes the DocumentProcessor with a text splitter and OpenAI embeddings.

        Attributes:
        - text_splitter: An instance of RecursiveCharacterTextSplitter with specified chunk size and overlap.
        - embeddings: An instance of OpenAIEmbeddings used for embedding documents.
        """
        load_dotenv()
        self.model = model
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size =1000,
                                                        chunk_overlap=200)
        # self.openai_model = OpenAIEmbedding(api_key=st.secrets["API_KEY"])
        self.openai_model = OpenAIEmbedding(api_key=os.getenv("API_KEY"))
        # self.openai_model = OpenAIEmbedding(api_key=api_key)
        
    def process_documents(self, documents):
        """
        Processes a list of documents by splitting them into smaller chunks and a vector store.
        Args:
        - documents (list of str): A list of documents to be processed.

        Returns:
        - tuples: A tuple containing:
            - splits (list of str): The list of split document chunks.
            - vector_store (FAISS): A FAISS vector store created from the split document chunks and their embeddings.
        """
        

        splits = self.text_splitter.split_documents(documents)
        embeddings = []
        for chunk in splits:
            
            embedd = self.openai_model.embed_documents(chunk.page_content)
            embeddings.extend(embedd)
            
        embedding_array = np.array(embeddings, dtype="float32") 
        dimension = embedding_array.shape[1]
        vector_store = faiss.IndexFlatL2(dimension)
        vector_store.add(embedding_array)
        
        self.documents = splits

        return splits, vector_store, self.openai_model, self.documents
    
    def create_embeddings_batch(self, texts, batch_size=32):
        """
        Creates embeddings for a list of texts in batches.

        Args:
        - texts (list of str): A list of texts to be embedded.
        - batch_size (int, optional): The number of texts to process in each batch.
        
        Returns:
        - numpy.ndarrays: An array of embeddings for hte input texts.
        """

        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = np.array([self.get_embedding(text) for text in batch])
            embeddings.extend(batch_embeddings)
        return np.array(embeddings)
    
    def compute_similarity_matrix(self, embeddings):
        """
        Computes a cosine similarity matrix for a given set of embeddings.
        Args:
        - embeddings (numpy.ndarray): An array of embeddigs.

        Returns:
        - numpy.ndarray: A cosine similarity matrix for the embeddding provided.
        """
        if embeddings.ndim ==1:
            embeddings = embeddings.reshape(1,-1)
        
        
        return cosine_similarity(embeddings)