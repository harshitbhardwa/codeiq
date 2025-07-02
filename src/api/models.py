from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    """Request model for code analysis."""
    file_path: Optional[str] = Field(None, description="Path to specific file to analyze")
    repository_path: Optional[str] = Field(None, description="Path to repository to analyze")
    language: Optional[str] = Field(None, description="Programming language filter")
    include_metrics: bool = Field(True, description="Include complexity metrics")
    include_embeddings: bool = Field(True, description="Generate embeddings for vector search")

class SearchRequest(BaseModel):
    """Request model for code search."""
    query: str = Field(..., description="Search query")
    search_type: str = Field("semantic", description="Search type: semantic, function_name, complexity")
    top_k: int = Field(5, description="Number of top results to return")
    language_filter: Optional[str] = Field(None, description="Filter by programming language")
    min_complexity: Optional[float] = Field(None, description="Minimum complexity threshold")
    max_complexity: Optional[float] = Field(None, description="Maximum complexity threshold")

class AlertRequest(BaseModel):
    """Request model for alert analysis."""
    alert_type: str = Field(..., description="Type of alert")
    alert_message: str = Field(..., description="Alert message")
    file_path: Optional[str] = Field(None, description="Related file path")
    line_number: Optional[int] = Field(None, description="Related line number")
    severity: str = Field("medium", description="Alert severity: low, medium, high, critical")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class FunctionInfo(BaseModel):
    """Model for function information."""
    name: str
    position: Dict[str, int]
    parameters: List[str]
    complexity: int
    body_text: str

class ClassInfo(BaseModel):
    """Model for class information."""
    name: str
    position: Dict[str, int]
    methods: List[FunctionInfo]
    complexity: int
    body_text: str

class ImportInfo(BaseModel):
    """Model for import information."""
    text: str
    position: Dict[str, int]
    type: str

class MetricsInfo(BaseModel):
    """Model for code metrics."""
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    average_complexity: float

class AnalysisResult(BaseModel):
    """Model for analysis result."""
    file_path: str
    language: str
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[ImportInfo]
    metrics: MetricsInfo
    analysis_timestamp: datetime

class SearchResult(BaseModel):
    """Model for search result."""
    file_path: str
    language: str
    similarity_score: Optional[float] = None
    rank: Optional[int] = None
    matched_function: Optional[FunctionInfo] = None
    complexity_score: Optional[float] = None
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[ImportInfo]
    metrics: MetricsInfo

class AlertAnalysisResult(BaseModel):
    """Model for alert analysis result."""
    alert_id: str
    alert_type: str
    alert_message: str
    severity: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    related_code: List[SearchResult]
    suggested_fixes: List[str]
    analysis_timestamp: datetime

class DatabaseStats(BaseModel):
    """Model for database statistics."""
    total_analysis_results: int
    total_alerts: int
    language_distribution: Dict[str, int]
    recent_analysis_results: int

class VectorIndexStats(BaseModel):
    """Model for vector index statistics."""
    total_vectors: int
    dimension: int
    index_type: str
    metadata_count: int

class HealthCheck(BaseModel):
    """Model for health check response."""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    vector_index_loaded: bool
    supported_languages: List[str]

class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str
    message: str
    timestamp: datetime
    request_id: Optional[str] = None 