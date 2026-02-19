"""Vector database integration using ChromaDB."""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from config import settings
from llm_client import llm_client
from document_processor import document_processor
from loguru import logger
import hashlib


class VectorStore:
    """Vector store for EU AI Act documents and retrieval."""
    
    def __init__(self):
        """Initialize ChromaDB vector store."""
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # EU AI Act collection
        self.collection_name = "eu_ai_act"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "EU AI Act document chunks"}
        )
        
        logger.info(f"Vector store initialized: {self.collection.count()} documents")
    
    def _generate_chunk_id(self, text: str, index: int) -> str:
        """Generate unique ID for chunk."""
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"eu_ai_act_chunk_{index}_{text_hash}"
    
    def index_eu_ai_act(self, force_reindex: bool = False) -> int:
        """Index EU AI Act PDF into vector database.
        
        Args:
            force_reindex: Force re-indexing even if already indexed
            
        Returns:
            Number of chunks indexed
        """
        pdf_path = Path(settings.eu_ai_act_pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"EU AI Act PDF not found: {pdf_path}")
        
        # Check if already indexed
        if self.collection.count() > 0 and not force_reindex:
            logger.info(f"EU AI Act already indexed ({self.collection.count()} chunks). Use force_reindex=True to re-index.")
            return self.collection.count()
        
        logger.info(f"Indexing EU AI Act from: {pdf_path}")
        
        # Process document
        full_text, chunks = document_processor.process_document(pdf_path)
        
        if not chunks:
            raise ValueError("No chunks extracted from EU AI Act PDF")
        
        # Clear existing if force reindex
        if force_reindex and self.collection.count() > 0:
            logger.info("Clearing existing index...")
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "EU AI Act document chunks"}
            )
        
        # Generate embeddings and add to collection
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        
        embeddings = []
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            embedding = llm_client.get_embedding(chunk)
            embeddings.append(embedding)
            ids.append(self._generate_chunk_id(chunk, i))
            documents.append(chunk)
            metadatas.append({
                "chunk_index": i,
                "source": "EU_AI_ACT.pdf",
                "total_chunks": len(chunks)
            })
            
            if (i + 1) % 10 == 0:
                logger.info(f"Processed {i + 1}/{len(chunks)} chunks")
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully indexed {len(chunks)} chunks from EU AI Act")
        return len(chunks)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """Search vector database for relevant chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            Tuple of (documents, metadatas, distances)
        """
        # Generate query embedding
        query_embedding = llm_client.get_embedding(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata if filter_metadata else None
        )
        
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        logger.info(f"Retrieved {len(documents)} documents for query")
        
        return documents, metadatas, distances
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "collection_name": self.collection_name,
            "total_documents": self.collection.count(),
            "indexed": self.collection.count() > 0
        }


# Global vector store instance
vector_store = VectorStore()
