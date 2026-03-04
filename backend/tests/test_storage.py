"""Unit tests for storage service."""
import pytest
import pandas as pd
from app.services.storage import FileStorage


@pytest.mark.unit
class TestFileStorage:
    """Test cases for FileStorage."""
    
    def test_store_and_retrieve_dataframe(self):
        """Test storing and retrieving a DataFrame."""
        storage = FileStorage()
        file_id = "test_123"
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        
        storage.save(
            file_id=file_id,
            filename="test.csv",
            uploaded_at="2024-01-01T00:00:00",
            metadata={"row_count": 3, "column_count": 2},
            dataframe=df
        )
        
        assert storage.exists(file_id)
        retrieved_df = storage.get_dataframe(file_id)
        assert retrieved_df is not None
        pd.testing.assert_frame_equal(df, retrieved_df)
        
        # Cleanup
        storage.delete(file_id)
    
    def test_get_metadata(self):
        """Test retrieving file metadata."""
        storage = FileStorage()
        file_id = "test_456"
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        
        storage.save(
            file_id=file_id,
            filename="test.csv",
            uploaded_at="2024-01-01T00:00:00",
            metadata={"row_count": 2, "column_count": 2},
            dataframe=df
        )
        metadata = storage.get_metadata(file_id)
        
        assert metadata is not None
        assert metadata["row_count"] == 2
        assert metadata["column_count"] == 2
        
        # Cleanup
        storage.delete(file_id)
    
    def test_delete_file(self):
        """Test deleting a file."""
        storage = FileStorage()
        file_id = "test_789"
        df = pd.DataFrame({'A': [1]})
        
        storage.save(
            file_id=file_id,
            filename="test.csv",
            uploaded_at="2024-01-01T00:00:00",
            metadata={},
            dataframe=df
        )
        assert storage.exists(file_id)
        
        storage.delete(file_id)
        assert not storage.exists(file_id)
    
    def test_nonexistent_file(self):
        """Test operations on non-existent file."""
        storage = FileStorage()
        file_id = "nonexistent"
        
        assert not storage.exists(file_id)
        assert storage.get_dataframe(file_id) is None
        assert storage.get_metadata(file_id) is None
