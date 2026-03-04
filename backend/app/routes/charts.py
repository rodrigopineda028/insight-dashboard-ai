"""Chart data processing routes."""
from fastapi import APIRouter, HTTPException

from app.models.requests import ChartDataRequest
from app.models.responses import ChartDataResponse
from app.services.chart_service import chart_service
from app.services.storage import file_storage

router = APIRouter()


@router.post("/chart-data", response_model=ChartDataResponse)
async def get_chart_data(request: ChartDataRequest):
    """
    Get processed data for a specific chart.
    
    Applies aggregations and formatting based on chart type.
    """
    # Get DataFrame from storage
    if not file_storage.exists(request.file_id):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    df = file_storage.get_dataframe(request.file_id)
    if df is None:
        raise HTTPException(status_code=404, detail="DataFrame no encontrado")
    
    # Validate columns exist
    if request.x_axis not in df.columns:
        raise HTTPException(status_code=400, detail=f"Columna '{request.x_axis}' no existe")
    
    if request.y_axis and request.y_axis not in df.columns:
        raise HTTPException(status_code=400, detail=f"Columna '{request.y_axis}' no existe")
    
    # Process data using chart service
    try:
        data = chart_service.get_chart_data(
            df=df,
            chart_type=request.chart_type,
            x_axis=request.x_axis,
            y_axis=request.y_axis,
            aggregation=request.aggregation
        )
        
        return ChartDataResponse(
            chart_type=request.chart_type,
            x_axis=request.x_axis,
            y_axis=request.y_axis,
            data=data,
            total_points=len(data)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar datos: {str(e)}"
        )
