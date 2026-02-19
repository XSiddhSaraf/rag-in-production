"""RAG pipeline for analyzing technical documents against EU AI Act."""

from typing import Dict, Any, List
from pathlib import Path
from vector_store import vector_store
from llm_client import llm_client
from document_processor import document_processor
from models import ProjectAnalysis, Risk, RiskLevel
from loguru import logger


class RAGPipeline:
    """RAG pipeline for EU AI Act compliance analysis."""
    
    def __init__(self, top_k_retrieval: int = 5):
        """Initialize RAG pipeline.
        
        Args:
            top_k_retrieval: Number of context chunks to retrieve
        """
        self.top_k = top_k_retrieval
    
    def _reformulate_query(self, text_snippet: str) -> str:
        """Create search query from technical document snippet.
        
        Args:
            text_snippet: Snippet from technical document
            
        Returns:
            Reformulated search query
        """
        # Extract key terms for better retrieval
        # For now, use a simple approach - could be enhanced with LLM
        query_parts = [
            "AI system",
            "machine learning",
            "high risk AI",
            "prohibited AI practices",
            "artificial intelligence regulation"
        ]
        
        # Combine with document snippet
        query = f"{text_snippet[:500]} {' '.join(query_parts)}"
        return query
    
    def retrieve_context(self, technical_doc_text: str) -> List[str]:
        """Retrieve relevant EU AI Act context.
        
        Args:
            technical_doc_text: Technical document text
            
        Returns:
            List of relevant context chunks
        """
        logger.info("Retrieving relevant EU AI Act context...")
        
        # Create query from technical document
        query = self._reformulate_query(technical_doc_text)
        
        # Retrieve from vector store
        documents, metadatas, distances = vector_store.search(
            query=query,
            top_k=self.top_k
        )
        
        logger.info(f"Retrieved {len(documents)} context chunks")
        for i, (doc, dist) in enumerate(zip(documents[:3], distances[:3])):
            logger.debug(f"Context {i+1} (distance: {dist:.4f}): {doc[:100]}...")
        
        return documents
    
    def analyze_document(self, file_path: Path) -> ProjectAnalysis:
        """Analyze technical document for AI compliance.
        
        Args:
            file_path: Path to technical document
            
        Returns:
            ProjectAnalysis object
        """
        logger.info(f"Starting RAG analysis for: {file_path}")
        
        # Step 1: Process document
        full_text, chunks = document_processor.process_document(file_path)
        
        # Step 2: Retrieve relevant EU AI Act context
        eu_context = self.retrieve_context(full_text)
        
        # Step 3: Analyze with LLM
        analysis_result = llm_client.analyze_project(
            technical_doc_text=full_text,
            eu_context=eu_context
        )
        
        logger.info(f"Analysis complete: {analysis_result.get('project_name', 'Unknown')}")
        
        # Step 4: Convert to ProjectAnalysis model
        project_analysis = self._convert_to_model(analysis_result)
        
        return project_analysis
    
    def _convert_to_model(self, llm_response: Dict[str, Any]) -> ProjectAnalysis:
        """Convert LLM response to ProjectAnalysis model.
        
        Args:
            llm_response: Raw LLM response dict
            
        Returns:
            ProjectAnalysis object
        """
        # Parse high risks
        high_risks = []
        for risk_data in llm_response.get('high_risks', []):
            high_risks.append(Risk(
                description=risk_data.get('description', ''),
                category=risk_data.get('category', 'Unknown'),
                level=RiskLevel.HIGH,
                eu_act_reference=risk_data.get('eu_act_reference'),
                confidence_score=risk_data.get('confidence_score')
            ))
        
        # Parse low risks
        low_risks = []
        for risk_data in llm_response.get('low_risks', []):
            low_risks.append(Risk(
                description=risk_data.get('description', ''),
                category=risk_data.get('category', 'Unknown'),
                level=RiskLevel.LOW,
                eu_act_reference=risk_data.get('eu_act_reference'),
                confidence_score=risk_data.get('confidence_score')
            ))
        
        return ProjectAnalysis(
            project_name=llm_response.get('project_name', 'Unknown Project'),
            description=llm_response.get('description', ''),
            contains_ai=llm_response.get('contains_ai', False),
            ai_confidence=llm_response.get('ai_confidence', 0.0),
            high_risks=high_risks,
            low_risks=low_risks,
            metadata={
                'total_risks': len(high_risks) + len(low_risks),
                'high_risk_count': len(high_risks),
                'low_risk_count': len(low_risks)
            }
        )


# Global RAG pipeline instance
rag_pipeline = RAGPipeline()
