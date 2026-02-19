"""Unit tests for RAG pipeline."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from rag_pipeline import RAGPipeline
from models import ProjectAnalysis, Risk, RiskLevel


@pytest.fixture
def rag_pipeline():
    """Create RAG pipeline instance."""
    return RAGPipeline(top_k_retrieval=3)


@pytest.fixture
def sample_document_text():
    """Sample technical document text."""
    return """
    This project implements a facial recognition system for automated 
    border control. The system uses deep learning models to identify 
    individuals from camera feeds. It processes biometric data in real-time 
    and makes automated decisions about entry permissions.
    """


@pytest.fixture
def sample_eu_context():
    """Sample EU AI Act context chunks."""
    return [
        "Article 5: Prohibited AI Practices - AI systems for biometric identification in public spaces are prohibited.",
        "Article 6: High-Risk AI Systems - AI systems used in border control are classified as high-risk.",
        "Article 9: Transparency obligations for providers of high-risk AI systems."
    ]


def test_reformulate_query(rag_pipeline, sample_document_text):
    """Test query reformulation."""
    query = rag_pipeline._reformulate_query(sample_document_text)
    
    assert isinstance(query, str)
    assert len(query) > 0
    assert "AI system" in query or "machine learning" in query


@patch('rag_pipeline.vector_store.search')
def test_retrieve_context(mock_search, rag_pipeline, sample_document_text, sample_eu_context):
    """Test context retrieval."""
    # Mock vector store search
    mock_search.return_value = (sample_eu_context, [{}, {}, {}], [0.1, 0.2, 0.3])
    
    context = rag_pipeline.retrieve_context(sample_document_text)
    
    assert isinstance(context, list)
    assert len(context) == 3
    assert context == sample_eu_context
    mock_search.assert_called_once()


def test_convert_to_model(rag_pipeline):
    """Test conversion of LLM response to ProjectAnalysis model."""
    llm_response = {
        "project_name": "Border Control AI",
        "description": "Facial recognition for border control",
        "contains_ai": True,
        "ai_confidence": 0.95,
        "high_risks": [
            {
                "description": "Biometric identification in public spaces",
                "category": "Prohibited AI",
                "eu_act_reference": "Article 5",
                "confidence_score": 0.9
            }
        ],
        "low_risks": [
            {
                "description": "Data processing transparency requirements",
                "category": "Transparency",
                "eu_act_reference": "Article 9",
                "confidence_score": 0.7
            }
        ]
    }
    
    result = rag_pipeline._convert_to_model(llm_response)
    
    assert isinstance(result, ProjectAnalysis)
    assert result.project_name == "Border Control AI"
    assert result.contains_ai == True
    assert result.ai_confidence == 0.95
    assert len(result.high_risks) == 1
    assert len(result.low_risks) == 1
    
    # Check high risk
    assert result.high_risks[0].description == "Biometric identification in public spaces"
    assert result.high_risks[0].level == RiskLevel.HIGH
    assert result.high_risks[0].eu_act_reference == "Article 5"
    
    # Check low risk
    assert result.low_risks[0].description == "Data processing transparency requirements"
    assert result.low_risks[0].level == RiskLevel.LOW


@patch('rag_pipeline.document_processor.process_document')
@patch('rag_pipeline.vector_store.search')
@patch('rag_pipeline.llm_client.analyze_project')
def test_analyze_document_integration(
    mock_analyze,
    mock_search,
    mock_process,
    rag_pipeline,
    sample_document_text,
    sample_eu_context
):
    """Test full document analysis pipeline."""
    # Mock document processor
    mock_process.return_value = (sample_document_text, [sample_document_text])
    
    # Mock vector store
    mock_search.return_value = (sample_eu_context, [{}, {}, {}], [0.1, 0.2, 0.3])
    
    # Mock LLM analysis
    mock_analyze.return_value = {
        "project_name": "Test Project",
        "description": "Test description",
        "contains_ai": True,
        "ai_confidence": 0.9,
        "high_risks": [],
        "low_risks": []
    }
    
    # Run analysis
    result = rag_pipeline.analyze_document(Path("test.pdf"))
    
    # Verify calls
    mock_process.assert_called_once()
    mock_search.assert_called_once()
    mock_analyze.assert_called_once()
    
    # Verify result
    assert isinstance(result, ProjectAnalysis)
    assert result.project_name == "Test Project"
    assert result.contains_ai == True


def test_analyze_document_no_ai(rag_pipeline):
    """Test analysis of document without AI components."""
    with patch('rag_pipeline.document_processor.process_document') as mock_process, \
         patch('rag_pipeline.vector_store.search') as mock_search, \
         patch('rag_pipeline.llm_client.analyze_project') as mock_analyze:
        
        # Mock non-AI document
        mock_process.return_value = ("Simple web application", ["Simple web application"])
        mock_search.return_value = ([], [], [])
        mock_analyze.return_value = {
            "project_name": "Web App",
            "description": "Basic website",
            "contains_ai": False,
            "ai_confidence": 0.1,
            "high_risks": [],
            "low_risks": []
        }
        
        result = rag_pipeline.analyze_document(Path("test.pdf"))
        
        assert result.contains_ai == False
        assert result.ai_confidence < 0.5
        assert len(result.high_risks) == 0
        assert len(result.low_risks) == 0
