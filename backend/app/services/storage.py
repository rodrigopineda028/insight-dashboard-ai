"""File storage service for uploaded files and DataFrames."""
from typing import Dict

import pandas as pd


class FileStorage:
    """In-memory file storage (use Redis/DB in production)."""
    
    def __init__(self):
        self._storage: Dict[str, dict] = {}
    
    def save(self, file_id: str, filename: str, uploaded_at: str, metadata: dict, dataframe: pd.DataFrame) -> None:
        """Save file data to storage."""
        self._storage[file_id] = {
            "id": file_id,
            "filename": filename,
            "uploaded_at": uploaded_at,
            "metadata": metadata,
            "dataframe": dataframe,
        }
    
    def get(self, file_id: str) -> dict:
        """Get file data from storage."""
        return self._storage.get(file_id, {})
    
    def get_dataframe(self, file_id: str) -> pd.DataFrame | None:
        """Get DataFrame from storage."""
        file_data = self._storage.get(file_id)
        return file_data.get("dataframe") if file_data else None
    
    def get_metadata(self, file_id: str) -> dict | None:
        """Get metadata from storage."""
        file_data = self._storage.get(file_id)
        return file_data.get("metadata") if file_data else None
    
    def exists(self, file_id: str) -> bool:
        """Check if file exists in storage."""
        return file_id in self._storage
    
    def delete(self, file_id: str) -> None:
        """Delete file from storage."""
        if file_id in self._storage:
            del self._storage[file_id]
    
    def clear(self) -> None:
        """Clear all storage."""
        self._storage.clear()


# Singleton instance
file_storage = FileStorage()
