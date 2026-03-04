"""Request models for API endpoints."""
from typing import Literal

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    """Request model for file analysis."""
    file_id: str


class ChartDataRequest(BaseModel):
    """Request model for chart data generation."""
    file_id: str
    chart_type: Literal["bar", "line", "pie", "scatter"]
    x_axis: str
    y_axis: str | None = None
    aggregation: Literal["sum", "count", "avg", "none"] = "none"


class QueryRequest(BaseModel):
    """Request model for natural language query."""
    file_id: str
    query: str
