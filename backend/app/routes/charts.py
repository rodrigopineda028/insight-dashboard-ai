"""Chart data processing routes."""
from typing import Any, Dict, List, Literal

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.routes.upload import file_storage

router = APIRouter()


class ChartDataRequest(BaseModel):
    file_id: str
    chart_type: Literal["bar", "line", "pie", "scatter"]
    x_axis: str
    y_axis: str | None = None
    aggregation: Literal["sum", "count", "avg", "none"] = "none"


def aggregate_data(df: pd.DataFrame, x_col: str, y_col: str | None, agg_type: str) -> List[Dict[str, Any]]:
    """Aggregate data based on chart parameters."""
    
    if agg_type == "count":
        # Count occurrences of each category
        result = df[x_col].value_counts().reset_index()
        result.columns = [x_col, "count"]
        return result.to_dict(orient="records")
    
    elif agg_type == "none" and y_col:
        # No aggregation, return as is (for scatter or line charts with direct values)
        result = df[[x_col, y_col]].dropna()
        return result.to_dict(orient="records")
    
    elif agg_type in ["sum", "avg"] and y_col:
        # Group by x_col and aggregate y_col
        grouped = df.groupby(x_col)[y_col]
        
        if agg_type == "sum":
            result = grouped.sum().reset_index()
        else:  # avg
            result = grouped.mean().reset_index()
        
        result.columns = [x_col, y_col]
        return result.to_dict(orient="records")
    
    else:
        # Default: just return unique values
        result = df[x_col].value_counts().reset_index()
        result.columns = [x_col, "value"]
        return result.to_dict(orient="records")


def process_pie_chart(df: pd.DataFrame, column: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Process data for pie chart (top N categories)."""
    counts = df[column].value_counts().head(limit)
    result = counts.reset_index()
    result.columns = ["name", "value"]
    return result.to_dict(orient="records")


def process_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, agg_type: str) -> List[Dict[str, Any]]:
    """Process data for bar chart."""
    return aggregate_data(df, x_col, y_col, agg_type)


def process_line_chart(df: pd.DataFrame, x_col: str, y_col: str, agg_type: str) -> List[Dict[str, Any]]:
    """Process data for line chart (typically temporal data)."""
    data = aggregate_data(df, x_col, y_col, agg_type)
    
    # Sort by x_axis (important for line charts to show trends)
    if data:
        try:
            # Try to sort as datetime if possible
            df_temp = pd.DataFrame(data)
            df_temp[x_col] = pd.to_datetime(df_temp[x_col], errors='ignore')
            data = df_temp.sort_values(x_col).to_dict(orient="records")
        except:
            # If not datetime, sort as is
            data = sorted(data, key=lambda x: x[x_col])
    
    return data


def process_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str) -> List[Dict[str, Any]]:
    """Process data for scatter chart."""
    # For scatter, we want individual points, no aggregation
    # Limit to 500 points for performance
    result = df[[x_col, y_col]].dropna().head(500)
    return result.to_dict(orient="records")


@router.post("/chart-data")
async def get_chart_data(request: ChartDataRequest):
    """
    Get processed data for a specific chart.
    
    Applies aggregations and formatting based on chart type.
    """
    # Get file from storage
    if request.file_id not in file_storage:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    file_data = file_storage[request.file_id]
    df = file_data["dataframe"]
    
    # Validate columns exist
    if request.x_axis not in df.columns:
        raise HTTPException(status_code=400, detail=f"Columna '{request.x_axis}' no existe")
    
    if request.y_axis and request.y_axis not in df.columns:
        raise HTTPException(status_code=400, detail=f"Columna '{request.y_axis}' no existe")
    
    # Process based on chart type
    try:
        if request.chart_type == "pie":
            data = process_pie_chart(df, request.x_axis)
        elif request.chart_type == "bar":
            if not request.y_axis:
                raise HTTPException(status_code=400, detail="Bar chart requiere y_axis")
            data = process_bar_chart(df, request.x_axis, request.y_axis, request.aggregation)
        elif request.chart_type == "line":
            if not request.y_axis:
                raise HTTPException(status_code=400, detail="Line chart requiere y_axis")
            data = process_line_chart(df, request.x_axis, request.y_axis, request.aggregation)
        elif request.chart_type == "scatter":
            if not request.y_axis:
                raise HTTPException(status_code=400, detail="Scatter chart requiere y_axis")
            data = process_scatter_chart(df, request.x_axis, request.y_axis)
        else:
            raise HTTPException(status_code=400, detail="Tipo de gráfico no soportado")
        
        return {
            "chart_type": request.chart_type,
            "x_axis": request.x_axis,
            "y_axis": request.y_axis,
            "data": data,
            "total_points": len(data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar datos: {str(e)}"
        )
