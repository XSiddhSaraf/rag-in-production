"""Pydantic models for request/response schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    """Risk level classification."""
    HIGH = "high"
    LOW = "low"
    NONE = "none"


class Risk(BaseModel):
    """Individual risk item."""
    description: str
    category: str
    level: RiskLevel
    eu_act_reference: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ProjectAnalysis(BaseModel):
    """Project analysis results."""
    project_name: str
    description: str
    contains_ai: bool
    ai_confidence: float = Field(..., ge=0.0, le=1.0)
    high_risks: List[Risk] = []
    low_risks: List[Risk] = []
    metadata: Dict[str, Any] = {}


class EvaluationMetrics(BaseModel):
    """RAG evaluation metrics."""
    faithfulness: Optional[float] = Field(None, ge=0.0, le=1.0)
    answer_relevance: Optional[float] = Field(None, ge=0.0, le=1.0)
    context_precision: Optional[float] = Field(None, ge=0.0, le=1.0)
    context_recall: Optional[float] = Field(None, ge=0.0, le=1.0)
    overall_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class LLMJudgeResult(BaseModel):
    """LLM-as-a-judge evaluation result."""
    accuracy_score: float = Field(..., ge=0.0, le=1.0)
    completeness_score: float = Field(..., ge=0.0, le=1.0)
    consistency_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


class AnalysisResult(BaseModel):
    """Complete analysis result including evaluation."""
    job_id: str
    status: JobStatus
    project_analysis: Optional[ProjectAnalysis] = None
    evaluation_metrics: Optional[EvaluationMetrics] = None
    llm_judge_result: Optional[LLMJudgeResult] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class UploadResponse(BaseModel):
    """Response from file upload endpoint."""
    job_id: str
    status: JobStatus
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    vector_db_status: str
    llm_status: str
