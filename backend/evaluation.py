"""Evaluation framework with RAG metrics and LLM-as-a-judge."""

from typing import Dict, Any, List, Optional
from models import EvaluationMetrics, LLMJudgeResult, ProjectAnalysis
from llm_client import llm_client
from config import settings
from loguru import logger
import asyncio


class EvaluationFramework:
    """Evaluation framework for RAG pipeline."""
    
    def __init__(self):
        """Initialize evaluation framework."""
        self.enabled_metrics = settings.eval_metrics_list
        self.llm_judge_enabled = settings.llm_judge_enabled
    
    def calculate_faithfulness(
        self,
        context: List[str],
        analysis: ProjectAnalysis
    ) -> float:
        """Calculate faithfulness score (are claims grounded in context?).
        
        Args:
            context: Retrieved EU AI Act context
            analysis: Analysis result
            
        Returns:
            Faithfulness score (0-1)
        """
        # Simplified faithfulness check
        # In production, use RAGAS or more sophisticated approach
        
        # Check if risks mentioned have grounding in context
        context_text = " ".join(context).lower()
        
        grounded_count = 0
        total_claims = len(analysis.high_risks) + len(analysis.low_risks)
        
        if total_claims == 0:
            return 1.0  # No claims to verify
        
        for risk in analysis.high_risks + analysis.low_risks:
            # Check if key terms from risk appear in context
            risk_terms = risk.description.lower().split()
            common_terms = sum(1 for term in risk_terms if len(term) > 4 and term in context_text)
            
            if common_terms >= 2:  # At least 2 significant terms found
                grounded_count += 1
        
        score = grounded_count / total_claims
        logger.debug(f"Faithfulness: {grounded_count}/{total_claims} = {score:.2f}")
        return score
    
    def calculate_answer_relevance(
        self,
        analysis: ProjectAnalysis,
        technical_doc: str
    ) -> float:
        """Calculate answer relevance (does analysis address the document?).
        
        Args:
            analysis: Analysis result
            technical_doc: Original technical document
            
        Returns:
            Relevance score (0-1)
        """
        # Check if analysis description aligns with document
        doc_lower = technical_doc.lower()
        desc_lower = analysis.description.lower()
        
        # Simple overlap check
        desc_words = set(desc_lower.split())
        doc_words = set(doc_lower.split())
        
        common_words = desc_words & doc_words
        if len(desc_words) == 0:
            return 0.0
        
        overlap_ratio = len(common_words) / len(desc_words)
        
        # Boost if AI detection seems appropriate
        has_ai_terms = any(term in doc_lower for term in ['ai', 'machine learning', 'neural', 'model', 'algorithm'])
        if has_ai_terms == analysis.contains_ai:
            overlap_ratio = min(1.0, overlap_ratio * 1.2)
        
        logger.debug(f"Answer relevance: {overlap_ratio:.2f}")
        return min(1.0, overlap_ratio)
    
    def calculate_context_precision(
        self,
        context: List[str],
        analysis: ProjectAnalysis
    ) -> float:
        """Calculate context precision (is retrieved context relevant?).
        
        Args:
            context: Retrieved context chunks
            analysis: Analysis result
            
        Returns:
            Precision score (0-1)
        """
        # Check how many context chunks contributed to the analysis
        relevant_count = 0
        
        for ctx in context:
            ctx_lower = ctx.lower()
            
            # Check if any risk references this context
            for risk in analysis.high_risks + analysis.low_risks:
                if risk.eu_act_reference and risk.eu_act_reference.lower() in ctx_lower:
                    relevant_count += 1
                    break
        
        if len(context) == 0:
            return 0.0
        
        precision = relevant_count / len(context)
        logger.debug(f"Context precision: {relevant_count}/{len(context)} = {precision:.2f}")
        return precision
    
    def calculate_context_recall(
        self,
        context: List[str],
        analysis: ProjectAnalysis
    ) -> float:
        """Calculate context recall (was enough context retrieved?).
        
        Args:
            context: Retrieved context chunks
            analysis: Analysis result
            
        Returns:
            Recall score (0-1)
        """
        # Check if all identified risks have supporting context
        risks_with_support = 0
        total_risks = len(analysis.high_risks) + len(analysis.low_risks)
        
        if total_risks == 0:
            return 1.0
        
        context_text = " ".join(context).lower()
        
        for risk in analysis.high_risks + analysis.low_risks:
            if risk.eu_act_reference:
                # Has explicit reference
                risks_with_support += 1
            else:
                # Check if description terms appear in context
                risk_terms = risk.description.lower().split()
                common_terms = sum(1 for term in risk_terms if len(term) > 4 and term in context_text)
                if common_terms >= 2:
                    risks_with_support += 1
        
        recall = risks_with_support / total_risks
        logger.debug(f"Context recall: {risks_with_support}/{total_risks} = {recall:.2f}")
        return recall
    
    def evaluate_rag(
        self,
        context: List[str],
        analysis: ProjectAnalysis,
        technical_doc: str
    ) -> EvaluationMetrics:
        """Evaluate RAG pipeline with multiple metrics.
        
        Args:
            context: Retrieved EU AI Act context
            analysis: Analysis result
            technical_doc: Original technical document
            
        Returns:
            EvaluationMetrics object
        """
        logger.info("Calculating RAG evaluation metrics...")
        
        metrics = {}
        
        if "faithfulness" in self.enabled_metrics:
            metrics['faithfulness'] = self.calculate_faithfulness(context, analysis)
        
        if "answer_relevance" in self.enabled_metrics:
            metrics['answer_relevance'] = self.calculate_answer_relevance(analysis, technical_doc)
        
        if "context_precision" in self.enabled_metrics:
            metrics['context_precision'] = self.calculate_context_precision(context, analysis)
        
        if "context_recall" in self.enabled_metrics:
            metrics['context_recall'] = self.calculate_context_recall(context, analysis)
        
        # Calculate overall score
        if metrics:
            metrics['overall_score'] = sum(metrics.values()) / len(metrics)
        else:
            metrics['overall_score'] = 0.0
        
        logger.info(f"Evaluation metrics: {metrics}")
        
        return EvaluationMetrics(**metrics)
    
    def llm_as_judge(
        self,
        technical_doc: str,
        analysis: ProjectAnalysis,
        eu_context: List[str]
    ) -> Optional[LLMJudgeResult]:
        """Use LLM to judge analysis quality.
        
        Args:
            technical_doc: Original technical document
            analysis: Analysis result
            eu_context: Retrieved EU AI Act context
            
        Returns:
            LLMJudgeResult or None if disabled
        """
        if not self.llm_judge_enabled:
            return None
        
        logger.info("Running LLM-as-a-judge evaluation...")
        
        # Convert analysis to dict for LLM
        analysis_dict = analysis.model_dump()
        
        # Get LLM judgment
        judge_result = llm_client.judge_analysis(
            technical_doc=technical_doc,
            analysis_result=analysis_dict,
            eu_context=eu_context
        )
        
        llm_judge_result = LLMJudgeResult(**judge_result)
        
        logger.info(f"LLM Judge Score: {llm_judge_result.overall_score:.2f}")
        
        return llm_judge_result


# Global evaluation framework instance
evaluation_framework = EvaluationFramework()
