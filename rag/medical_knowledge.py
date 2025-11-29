"""
Medical Knowledge RAG System
Retrieves evidence-based medical information using ChromaDB
"""

import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict

class MedicalKnowledgeRAG:
    """RAG system for medical knowledge retrieval."""
    
    def __init__(self, persist_directory: str = "./rag/chroma_db"):
        """Initialize ChromaDB for medical knowledge."""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("medical_knowledge")
            print("✅ Loaded existing medical knowledge database")
        except:
            self.collection = self.client.create_collection(
                name="medical_knowledge",
                metadata={"description": "Medical guidelines and health information"}
            )
            print("✅ Created new medical knowledge database")
    
    def add_document(self, text: str, metadata: Dict, doc_id: str):
        """Add a document to the knowledge base."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
    
    def retrieve(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['documents'] or not results['documents'][0]:
            return []
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results['documents'][0]):
            formatted_results.append({
                'content': doc,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else 0
            })
        
        return formatted_results
    
    def get_context(self, query: str, n_results: int = 2) -> str:
        """
        Get formatted context for LLM prompt.
        
        Args:
            query: Search query
            n_results: Number of documents to retrieve
            
        Returns:
            Formatted context string
        """
        results = self.retrieve(query, n_results)
        
        if not results:
            return "No specific medical guidelines found for this query."
        
        context = "**Medical Guidelines (from RAG):**\n\n"
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source', 'Medical Database')
            context += f"{i}. [{source}]\n{result['content'][:500]}...\n\n"
        
        return context


# Testing
if __name__ == "__main__":
    rag = MedicalKnowledgeRAG()
    
    # Test retrieval
    print("Testing RAG system...\n")
    
    test_queries = [
        "What are the glucose target ranges?",
        "How to treat low blood sugar?",
        "Metformin and alcohol"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        context = rag.get_context(query)
        print(context)
        print("="*60)