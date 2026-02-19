"""Configuration management for the RAG application."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_embedding_deployment: str = "text-embedding-ada-002"
    
    # Vector Database Configuration
    vector_db_type: str = "chroma"  # chroma or azure_search
    chroma_persist_directory: str = "./data/chroma_db"
    
    # Azure Cognitive Search (optional)
    azure_search_endpoint: str = ""
    azure_search_api_key: str = ""
    azure_search_index_name: str = "eu-ai-act-index"
    
    # Application Configuration
    upload_folder: str = "./data/uploads"
    output_folder: str = "./data/outputs"
    max_file_size_mb: int = 50
    allowed_extensions: List[str] = ["pdf", "docx", "doc"]
    
    # EU AI Act Document Path
    eu_ai_act_pdf_path: str = "./data/EU_AI_ACT.pdf"
    
    # Evaluation Configuration
    eval_metrics: str = "faithfulness,answer_relevance,context_precision,context_recall"
    llm_judge_enabled: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def upload_path(self) -> Path:
        """Get upload folder as Path object."""
        path = Path(self.upload_folder)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def output_path(self) -> Path:
        """Get output folder as Path object."""
        path = Path(self.output_folder)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def chroma_path(self) -> Path:
        """Get Chroma DB path as Path object."""
        path = Path(self.chroma_persist_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def eval_metrics_list(self) -> List[str]:
        """Get evaluation metrics as list."""
        return [metric.strip() for metric in self.eval_metrics.split(",")]


# Global settings instance
settings = Settings()
