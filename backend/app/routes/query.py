"""Natural language query processing routes."""
from fastapi import APIRouter, HTTPException

from app.models.requests import QueryRequest
from app.models.responses import QueryResponse
from app.services.ai_service import ai_service
from app.services.storage import file_storage

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query and generate a chart suggestion.
    """
    # Check if file exists
    if not file_storage.exists(request.file_id):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    # Get file metadata
    metadata = file_storage.get_metadata(request.file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Metadata no encontrada")
    
    # Process query with AI
    suggestion = await ai_service.process_natural_language_query(
        metadata=metadata,
        query=request.query
    )
    
    return QueryResponse(
        file_id=request.file_id,
        query=request.query,
        suggestion=suggestion
    )
