"""Upload and file processing routes."""
import io
import uuid
from datetime import datetime
from typing import Dict

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()

# In-memory storage for uploaded files (use Redis/DB in production)
file_storage: Dict[str, dict] = {}

# Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return "." + filename.split(".")[-1].lower() if "." in filename else ""


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file format and size."""
    ext = get_file_extension(file.filename or "")
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}",
        )


def process_dataframe(df: pd.DataFrame) -> dict:
    """Extract metadata and statistics from DataFrame."""
    columns_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = int(df[col].count())
        
        col_info = {
            "name": col,
            "type": dtype,
            "non_null_count": non_null,
            "null_count": int(len(df) - non_null),
        }
        
        # Add statistics for numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["stats"] = {
                "min": float(df[col].min()) if not df[col].isna().all() else None,
                "max": float(df[col].max()) if not df[col].isna().all() else None,
                "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                "median": float(df[col].median()) if not df[col].isna().all() else None,
            }
        
        columns_info.append(col_info)
    
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": columns_info,
        "sample_data": df.head(5).to_dict(orient="records"),
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload CSV or Excel file and process it.
    
    Returns file metadata and basic statistics.
    """
    validate_file(file)
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo muy grande. Máximo {MAX_FILE_SIZE // (1024*1024)} MB",
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
    
    # Store in memory (including the DataFrame for later use)
    file_storage[file_id] = {
        "id": file_id,
        "filename": file.filename,
        "uploaded_at": datetime.utcnow().isoformat(),
        "metadata": metadata,
        "dataframe": df,
    }
    
    # Return metadata (without the raw DataFrame)
    return {
        "id": file_id,
        "filename": file.filename,
        "uploaded_at": file_storage[file_id]["uploaded_at"],
        "metadata": metadata,
    }


@router.get("/files/{file_id}/summary")
async def get_file_summary(file_id: str):
    """Get summary of previously uploaded file."""
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    stored = file_storage[file_id]
    return {
        "id": stored["id"],
        "filename": stored["filename"],
        "uploaded_at": stored["uploaded_at"],
        "metadata": stored["metadata"],
    }
