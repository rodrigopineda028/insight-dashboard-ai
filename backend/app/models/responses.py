"""Response models for API endpoints."""
from typing import Any, Dict, List

from pydantic import BaseModel


class ColumnStats(BaseModel):
    """Statistics for a numeric column."""
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    median: float | None = None
    std: float | None = None
    q25: float | None = None
    q75: float | None = None


class ColumnInfo(BaseModel):
    """Information about a DataFrame column."""
    name: str
    type: str
    non_null_count: int
    null_count: int
    missingness_pct: float
    cardinality: int
    stats: ColumnStats | None = None


class FileMetadata(BaseModel):
    """Metadata about an uploaded file."""
    row_count: int
    column_count: int
    columns: List[ColumnInfo]
    sample_data: List[Dict[str, Any]]


class UploadResponse(BaseModel):
    """Response model for file upload."""
    id: str
    filename: str
    uploaded_at: str
    metadata: FileMetadata


class ChartParameters(BaseModel):
    """Parameters for chart generation."""
    x_axis: str | None = None
    y_axis: str | None = None
    aggregation: str | None = None


class ChartSuggestion(BaseModel):
    """AI-generated chart suggestion."""
    title: str
    chart_type: str
    parameters: Dict[str, Any]
    insight: str


class AnalyzeResponse(BaseModel):
    """Response model for file analysis."""
    file_id: str
    suggestions: List[ChartSuggestion]
    total_suggestions: int


class ChartDataResponse(BaseModel):
    """Response model for chart data."""
    chart_type: str
    x_axis: str
    y_axis: str | None
    data: List[Dict[str, Any]]
    total_points: int


class QueryResponse(BaseModel):
    """Response model for natural language query."""
    file_id: str
    query: str
    suggestion: ChartSuggestion
