# Evaluation Framework Documentation

This document explains the RAG evaluation metrics and LLM-as-a-judge implementation used in the EU AI Act Compliance Analyzer.

## Overview

The evaluation framework provides quality assurance for the RAG pipeline by measuring:
1. **RAG Metrics**: How well the retrieval and generation components work
2. **LLM-as-a-Judge**: Independent assessment of analysis quality

## RAG Evaluation Metrics

### 1. Faithfulness (Groundedness)

**What it measures**: Whether the identified risks and AI components are grounded in the retrieved EU AI Act context.

**Calculation**:
- Checks if risk descriptions contain terms from the retrieved context
- Counts matches between risk keywords and context chunks
- Score = (Grounded risks) / (Total risks)

**Interpretation**:
- **High (≥0.8)**: Most risks are well-supported by EU AI Act context
- **Medium (0.6-0.8)**: Some risks may lack strong grounding
- **Low (<0.6)**: Analysis may be making unsupported claims

**Example**:
```
Context: "AI systems for biometric identification are prohibited..."
Risk: "Biometric identification system violates Article 5" ✓ Grounded
Risk: "Random claim not in context" ✗ Not grounded
```

### 2. Answer Relevance

**What it measures**: Whether the analysis addresses the actual content of the technical document.

**Calculation**:
- Compares project description with technical document content
- Calculates term overlap between description and document
- Boosts score if AI detection aligns with document content

**Interpretation**:
- **High (≥0.8)**: Analysis closely matches document content
- **Medium (0.6-0.8)**: Relevant but may miss some aspects
- **Low (<0.6)**: Analysis may be off-topic

### 3. Context Precision

**What it measures**: Whether the retrieved EU AI Act context chunks are relevant to the analysis.

**Calculation**:
- Counts how many retrieved chunks contributed to risk identification
- Checks for EU AI Act references in context
- Score = (Relevant context chunks) / (Total retrieved chunks)

**Interpretation**:
- **High (≥0.8)**: Retrieved context is highly relevant
- **Medium (0.6-0.8)**: Some irrelevant context retrieved
- **Low (<0.6)**: Retrieval may need tuning

### 4. Context Recall

**What it measures**: Whether enough EU AI Act context was retrieved to support all identified risks.

**Calculation**:
- Checks if each risk has supporting context
- Verifies all risks have EU AI Act references or matching terms
- Score = (Risks with support) / (Total risks)

**Interpretation**:
- **High (≥0.8)**: Sufficient context was retrieved
- **Medium (0.6-0.8)**: Some risks may lack context support
- **Low (<0.6)**: More context chunks may be needed

### Overall RAG Score

Average of all four metrics, providing a single quality indicator:

```python
overall_score = (faithfulness + answer_relevance + 
                 context_precision + context_recall) / 4
```

## LLM-as-a-Judge

### Purpose

Uses an LLM to independently evaluate the analysis quality, providing human-like assessment of results.

### Evaluation Criteria

#### 1. Accuracy Score (0-1)

**Evaluates**: Correctness of AI component identification and risk classification

**Questions**:
- Are identified AI systems actually present in the document?
- Are risks correctly categorized as high/low?
- Do classifications align with EU AI Act definitions?

#### 2. Completeness Score (0-1)

**Evaluates**: Coverage of all relevant aspects

**Questions**:
- Were all AI components in the document identified?
- Are all applicable EU AI Act articles referenced?
- Is the analysis thorough?

#### 3. Consistency Score (0-1)

**Evaluates**: Alignment with EU AI Act classifications

**Questions**:
- Do risk levels match EU AI Act categories?
- Are similar components classified consistently?
- Is terminology used correctly?

#### 4. Overall Judge Score

Average of the three criteria scores:

```python
overall_score = (accuracy + completeness + consistency) / 3
```

### Judge Reasoning

The LLM provides detailed reasoning for its scores, explaining:
- Which aspects were done well
- What could be improved
- Specific examples supporting the scores

## Using Evaluation Results

### Interpreting Scores

**Combined Score ≥ 0.8**: Excellent
- High confidence in results
- Safe to use for decision-making
- Minimal manual review needed

**Combined Score 0.6-0.8**: Good
- Generally reliable results
- Some manual review recommended
- May benefit from refinement

**Combined Score < 0.6**: Needs Review
- Results should be carefully reviewed
- Consider re-running analysis
- May indicate issues with document or pipeline

### Improving Scores

**Low Faithfulness**:
- Review prompt templates
- Increase number of retrieved chunks (top_k)
- Improve chunking strategy

**Low Answer Relevance**:
- Check document quality and format
- Verify document is relevant to EU AI Act
- Review project description extraction

**Low Context Precision**:
- Tune retrieval parameters
- Improve query reformulation
- Consider hybrid search (keyword + semantic)

**Low Context Recall**:
- Increase top_k retrieval parameter
- Verify EU AI Act is fully indexed
- Check if document references obscure AI concepts

**Low LLM Judge Scores**:
- Review and refine prompts
- Consider using different LLM temperature
- Add few-shot examples to prompts

## Automated vs Manual Evaluation

### When to Trust Automated Scores

- **High scores (>0.8)** across all metrics
- Standard technical documents
- Well-known AI technologies
- Clear EU AI Act applicability

### When Manual Review is Needed

- **Low scores (<0.6)** on any metric
- Novel or cutting-edge AI systems
- Ambiguous document content
- Edge cases in EU AI Act classification
- High-stakes compliance decisions

## Example Evaluation Report

```json
{
  "rag_metrics": {
    "faithfulness": 0.85,
    "answer_relevance": 0.92,
    "context_precision": 0.78,
    "context_recall": 0.88,
    "overall_score": 0.86
  },
  "llm_judge": {
    "accuracy_score": 0.90,
    "completeness_score": 0.85,
    "consistency_score": 0.88,
    "overall_score": 0.88,
    "reasoning": "The analysis correctly identified the facial recognition system as high-risk AI under Article 6. All major AI components were found. Classifications are consistent with EU AI Act definitions. Minor improvement: could reference Article 9 for transparency obligations."
  }
}
```

**Interpretation**: Excellent scores (>0.85) across the board. High confidence in results. The minor suggestion about Article 9 is noted for future improvements.

## Technical Implementation

### RAG Metrics Calculation

```python
from evaluation import evaluation_framework

metrics = evaluation_framework.evaluate_rag(
    context=retrieved_eu_context,
    analysis=analysis_result,
    technical_doc=document_text
)
```

### LLM-as-Judge Evaluation

```python
judge_result = evaluation_framework.llm_as_judge(
    technical_doc=document_text,
    analysis=analysis_result,
    eu_context=retrieved_context
)
```

## Configuration

Evaluation can be configured via environment variables:

```bash
# Enable/disable specific metrics
EVAL_METRICS=faithfulness,answer_relevance,context_precision,context_recall

# Enable/disable LLM-as-judge
LLM_JUDGE_ENABLED=true
```

## Best Practices

1. **Always review evaluation scores** before making compliance decisions
2. **Compare scores across similar documents** to identify patterns
3. **Track scores over time** to measure pipeline improvements
4. **Use combined RAG + Judge scores** for comprehensive assessment
5. **Document score thresholds** for your use case
6. **Periodically review low-scoring analyses** to improve prompts

## Future Enhancements

Planned improvements to the evaluation framework:

- **RAGAS integration**: Full RAGAS library implementation
- **Custom metrics**: Domain-specific evaluation criteria
- **Benchmark datasets**: Curated test cases with known outcomes
- **A/B testing**: Compare different prompt/model configurations
- **Human feedback**: Incorporate expert reviews into scores
