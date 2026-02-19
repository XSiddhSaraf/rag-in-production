"""FastAPI application for EU AI Act compliance analysis."""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Dict
import uuid
import shutil
from datetime import datetime

from config import settings
from models import (
    UploadResponse, AnalysisResult, HealthResponse,
    JobStatus, ProjectAnalysis, EvaluationMetrics, LLMJudgeResult
)
from vector_store import vector_store
from rag_pipeline import rag_pipeline
from evaluation import evaluation_framework
from excel_generator import excel_generator
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stderr, level=settings.log_level)

# Initialize FastAPI app
app = FastAPI(
    title="EU AI Act Compliance Analyzer",
    description="Production RAG application for analyzing technical documents against EU AI Act",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (use Redis/DB in production)
jobs: Dict[str, AnalysisResult] = {}


def process_analysis_job(job_id: str, file_path: Path):
    """Background task to process analysis job.
    
    Args:
        job_id: Job identifier
        file_path: Path to uploaded file
    """
    try:
        logger.info(f"Starting analysis job: {job_id}")
        
        # Update status
        jobs[job_id].status = JobStatus.PROCESSING
        
        # Step 1: Run RAG analysis
        logger.info("Step 1: Running RAG analysis...")
        analysis = rag_pipeline.analyze_document(file_path)
        jobs[job_id].project_analysis = analysis
        
        # Step 2: Retrieve context for evaluation
        from document_processor import document_processor
        full_text, _ = document_processor.process_document(file_path)
        eu_context = rag_pipeline.retrieve_context(full_text)
        
        # Step 3: Run evaluation metrics
        logger.info("Step 2: Running RAG evaluation...")
        eval_metrics = evaluation_framework.evaluate_rag(
            context=eu_context,
            analysis=analysis,
            technical_doc=full_text
        )
        jobs[job_id].evaluation_metrics = eval_metrics
        
        # Step 4: LLM-as-judge evaluation
        if settings.llm_judge_enabled:
            logger.info("Step 3: Running LLM-as-judge evaluation...")
            llm_judge = evaluation_framework.llm_as_judge(
                technical_doc=full_text,
                analysis=analysis,
                eu_context=eu_context
            )
            jobs[job_id].llm_judge_result = llm_judge
        
        # Step 5: Generate Excel file
        logger.info("Step 4: Generating Excel report...")
        excel_path = excel_generator.generate_excel(
            analysis=analysis,
            evaluation_metrics=eval_metrics,
            llm_judge=jobs[job_id].llm_judge_result,
            output_path=settings.output_path / f"{job_id}.xlsx"
        )
        
        # Update job status
        jobs[job_id].status = JobStatus.COMPLETED
        jobs[job_id].completed_at = datetime.now()
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.exception(f"Job {job_id} failed: {e}")
        jobs[job_id].status = JobStatus.FAILED
        jobs[job_id].error_message = str(e)
        jobs[job_id].completed_at = datetime.now()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting EU AI Act Compliance Analyzer...")
    
    # Ensure data directories exist
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.output_path.mkdir(parents=True, exist_ok=True)
    
    # Check if EU AI Act is indexed
    stats = vector_store.get_collection_stats()
    if not stats['indexed']:
        logger.warning("EU AI Act not indexed. Please index the document first.")
    else:
        logger.info(f"EU AI Act indexed: {stats['total_documents']} chunks")
    
    logger.info("Application ready!")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "EU AI Act Compliance Analyzer API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    vector_stats = vector_store.get_collection_stats()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        vector_db_status="ready" if vector_stats['indexed'] else "not_indexed",
        llm_status="ready"
    )


@app.post("/api/upload", response_model=UploadResponse, tags=["Analysis"])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload technical document for analysis.
    
    Args:
        file: Technical document (PDF or Word)
        
    Returns:
        UploadResponse with job_id
    """
    # Validate file type
    file_ext = Path(file.filename).suffix.lower().replace('.', '')
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = settings.upload_path / f"{job_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info(f"File uploaded: {file.filename} (Job: {job_id})")
    
    # Create job record
    jobs[job_id] = AnalysisResult(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.now()
    )
    
    # Schedule background processing
    background_tasks.add_task(process_analysis_job, job_id, file_path)
    
    return UploadResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="File uploaded successfully. Analysis started."
    )


@app.get("/api/analyze/{job_id}", response_model=AnalysisResult, tags=["Analysis"])
async def get_analysis(job_id: str):
    """Get analysis results for a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        AnalysisResult
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]


@app.get("/api/download/{job_id}", tags=["Analysis"])
async def download_excel(job_id: str):
    """Download Excel file for a completed job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Excel file
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job.status}"
        )
    
    excel_path = settings.output_path / f"{job_id}.xlsx"
    
    if not excel_path.exists():
        raise HTTPException(status_code=404, detail="Excel file not found")
    
    project_name = job.project_analysis.project_name.replace(' ', '_')
    filename = f"{project_name}_analysis.xlsx"
    
    return FileResponse(
        path=excel_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.post("/api/index-eu-act", tags=["Admin"])
async def index_eu_ai_act(force_reindex: bool = False):
    """Index EU AI Act PDF into vector database.
    
    Args:
        force_reindex: Force re-indexing
        
    Returns:
        Indexing status
    """
    try:
        num_chunks = vector_store.index_eu_ai_act(force_reindex=force_reindex)
        return {
            "status": "success",
            "message": f"Indexed {num_chunks} chunks from EU AI Act",
            "chunks": num_chunks
        }
    except Exception as e:
        logger.exception(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/vector-stats", tags=["Admin"])
async def get_vector_stats():
    """Get vector database statistics."""
    return vector_store.get_collection_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
