"""AI analysis routes using Claude."""
from fastapi import APIRouter, HTTPException

from app.models.requests import AnalyzeRequest
from app.models.responses import AnalyzeResponse
from app.services.ai_service import ai_service
from app.services.storage import file_storage

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_file(request: AnalyzeRequest):
    """
    Analyze uploaded file with Claude AI and get chart suggestions.
    """
    # Check if file exists
    if not file_storage.exists(request.file_id):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    # Get file metadata
    metadata = file_storage.get_metadata(request.file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Metadata no encontrada")
    
    # Analyze with Claude AI service
    suggestions = await ai_service.analyze_dataset(metadata)
    
    return AnalyzeResponse(
        file_id=request.file_id,
        suggestions=suggestions,
        total_suggestions=len(suggestions),
    )
