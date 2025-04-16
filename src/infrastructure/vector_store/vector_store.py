import os
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document

from config.config import settings

class VectorStore:
    """
    Vector store implementation using FAISS for efficient similarity search.
    This class provides methods to store, retrieve, and search embeddings.
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the vector store with embeddings model.
        
        Args:
            persist_directory: Directory to persist vector store. If None, uses config setting.
        """
        self.persist_directory = persist_directory or settings.VECTOR_DB_PATH
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
    
    def initialize_from_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Initialize the vector store from a list of texts.
        
        Args:
            texts: List of text strings to embed
            metadatas: Optional list of metadata dictionaries corresponding to each text
        """
        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        self.persist()
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dictionaries for each text
            
        Returns:
            List of IDs for the added texts
        """
        if self.vector_store is None:
            self.initialize_from_texts(texts, metadatas)
            return ["0"]  # Return dummy ID for initial texts
        
        return self.vector_store.add_texts(texts, metadatas)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Query string
            k: Number of results to return
            
        Returns:
            List of Documents most similar to the query
        """
        if self.vector_store is None:
            raise ValueError("Vector store is not initialized. Call initialize_from_texts first.")
        
        return self.vector_store.similarity_search(query, k=k)
    
    def persist(self) -> None:
        """
        Save the vector store to disk.
        """
        if self.vector_store is not None:
            self.vector_store.save_local(self.persist_directory)
    
    def load(self) -> bool:
        """
        Load the vector store from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            self.vector_store = FAISS.load_local(
                self.persist_directory, 
                self.embeddings
            )
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
        
    def clear(self) -> None:
        """
        Clear the vector store and remove persisted data.
        """
        self.vector_store = None
        for file in os.listdir(self.persist_directory):
            file_path = os.path.join(self.persist_directory, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

# Create a singleton instance
vector_store = VectorStore()

def get_vector_store() -> VectorStore:
    """
    Returns the vector store instance.
    This can be used as a FastAPI dependency.
    """
    return vector_store