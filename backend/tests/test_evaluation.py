"""Unit tests for evaluation framework."""

import pytest
from evaluation import EvaluationFramework
from models import ProjectAnalysis, Risk, RiskLevel, EvaluationMetrics, LLMJudgeResult


@pytest.fixture
def eval_framework():
    """Create evaluation framework instance."""
    return EvaluationFramework()


@pytest.fixture
def sample_analysis():
    """Sample project analysis."""
    return ProjectAnalysis(
        project_name="AI Border Control",
        description="Facial recognition system for border control",
        contains_ai=True,
        ai_confidence=0.95,
        high_risks=[
            Risk(
                description="Biometric identification system",
                category="Prohibited AI",
                level=RiskLevel.HIGH,
                eu_act_reference="Article 5",
                confidence_score=0.9
            )
        ],
        low_risks=[
            Risk(
                description="Data transparency requirements",
                category="Transparency",
                level=RiskLevel.LOW,
                eu_act_reference="Article 9",
                confidence_score=0.7
            )
        ]
    )


@pytest.fixture
def sample_context():
    """Sample EU AI Act context."""
    return [
        "Article 5: Prohibited AI Practices - biometric identification systems",
        "Article 6: High-risk AI systems in border control",
        "Article 9: Transparency obligations for providers"
    ]


def test_calculate_faithfulness_high(eval_framework, sample_context, sample_analysis):
    """Test faithfulness calculation with high score."""
    score = eval_framework.calculate_faithfulness(sample_context, sample_analysis)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Should be high since risks mention context terms


def test_calculate_faithfulness_no_risks(eval_framework, sample_context):
    """Test faithfulness with no risks."""
    analysis = ProjectAnalysis(
        project_name="Test",
        description="Test",
        contains_ai=False,
        ai_confidence=0.1,
        high_risks=[],
        low_risks=[]
    )
    
    score = eval_framework.calculate_faithfulness(sample_context, analysis)
    assert score == 1.0  # No claims to verify


def test_calculate_answer_relevance(eval_framework, sample_analysis):
    """Test answer relevance calculation."""
    technical_doc = """
    This facial recognition system uses AI for border control.
    It processes biometric data in real-time.
    """
    
    score = eval_framework.calculate_answer_relevance(sample_analysis, technical_doc)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_calculate_context_precision(eval_framework, sample_context, sample_analysis):
    """Test context precision calculation."""
    score = eval_framework.calculate_context_precision(sample_context, sample_analysis)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_calculate_context_precision_empty(eval_framework, sample_analysis):
    """Test context precision with no context."""
    score = eval_framework.calculate_context_precision([], sample_analysis)
    assert score == 0.0


def test_calculate_context_recall(eval_framework, sample_context, sample_analysis):
    """Test context recall calculation."""
    score = eval_framework.calculate_context_recall(sample_context, sample_analysis)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_evaluate_rag_complete(eval_framework, sample_context, sample_analysis):
    """Test complete RAG evaluation."""
    technical_doc = "Facial recognition AI system for border control with biometric data processing."
    
    metrics = eval_framework.evaluate_rag(
        context=sample_context,
        analysis=sample_analysis,
        technical_doc=technical_doc
    )
    
    assert isinstance(metrics, EvaluationMetrics)
    assert metrics.faithfulness is not None
    assert metrics.answer_relevance is not None
    assert metrics.context_precision is not None
    assert metrics.context_recall is not None
    assert metrics.overall_score is not None
    
    # Overall should be average
    calculated_avg = sum([
        metrics.faithfulness,
        metrics.answer_relevance,
        metrics.context_precision,
        metrics.context_recall
    ]) / 4
    
    assert abs(metrics.overall_score - calculated_avg) < 0.01


def test_llm_judge_disabled(eval_framework):
    """Test LLM-as-judge when disabled."""
    eval_framework.llm_judge_enabled = False
    
    result = eval_framework.llm_as_judge(
        technical_doc="test",
        analysis=ProjectAnalysis(
            project_name="Test",
            description="Test",
            contains_ai=False,
            ai_confidence=0.0,
            high_risks=[],
            low_risks=[]
        ),
        eu_context=[]
    )
    
    assert result is None
