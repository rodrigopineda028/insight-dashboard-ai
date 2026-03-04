"""Upload and file processing routes."""
import io
import uuid
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config.settings import settings
from app.models.responses import ColumnInfo, ColumnStats, FileMetadata, UploadResponse
from app.services.storage import file_storage

router = APIRouter()


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return "." + filename.split(".")[-1].lower() if "." in filename else ""


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file format and size."""
    ext = get_file_extension(file.filename or "")
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido. Use: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )


def process_dataframe(df: pd.DataFrame) -> FileMetadata:
    """Extract metadata and statistics from DataFrame."""
    columns_info = []
    total = len(df)
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = int(df[col].count())
        null_count = total - non_null
        
        stats = None
        # Add statistics for numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            stats = ColumnStats(
                min=float(df[col].min()) if not df[col].isna().all() else None,
                max=float(df[col].max()) if not df[col].isna().all() else None,
                mean=float(df[col].mean()) if not df[col].isna().all() else None,
                median=float(df[col].median()) if not df[col].isna().all() else None,
                std=float(df[col].std()) if not df[col].isna().all() else None,
                q25=float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
                q75=float(df[col].quantile(0.75)) if not df[col].isna().all() else None,
            )
        
        col_info = ColumnInfo(
            name=col,
            type=dtype,
            non_null_count=non_null,
            null_count=null_count,
            missingness_pct=round((null_count / total * 100), 2) if total > 0 else 0,
            cardinality=int(df[col].nunique()),
            stats=stats
        )
        
        columns_info.append(col_info)
    
    return FileMetadata(
        row_count=len(df),
        column_count=len(df.columns),
        columns=columns_info,
        sample_data=df.head(10).to_dict(orient="records"),
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload CSV or Excel file and process it.
    
    Returns file metadata and basic statistics.
    """
    validate_file(file)
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo muy grande. Máximo {settings.MAX_FILE_SIZE // (1024*1024)} MB",
        )
    
    # Parse file based on extension
    ext = get_file_extension(file.filename or "")
    
    try:
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(content))
        elif ext == ".xlsx":
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al procesar el archivo: {str(e)}"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Process DataFrame
    metadata = process_dataframe(df)
    uploaded_at = datetime.utcnow().isoformat()
    
    # Store in file storage service
    file_storage.save(
        file_id=file_id,
        filename=file.filename or "unknown",
        uploaded_at=uploaded_at,
        metadata=metadata.model_dump(),
        dataframe=df
    )
    
    return UploadResponse(
        id=file_id,
        filename=file.filename or "unknown",
        uploaded_at=uploaded_at,
        metadata=metadata
    )
