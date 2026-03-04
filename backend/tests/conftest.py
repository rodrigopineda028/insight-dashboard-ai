"""Pytest configuration and fixtures."""
import os
import pytest
from fastapi.testclient import TestClient
import pandas as pd

# Set test environment variables before importing app
os.environ['ANTHROPIC_API_KEY'] = 'test-api-key-for-testing'

from app.main import app
from app.services.storage import file_storage


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing."""
    return """Date,Product,Sales,Quantity
2024-01-01,ProductA,1000,10
2024-01-02,ProductB,2000,20
2024-01-03,ProductA,1500,15
2024-01-04,ProductC,3000,30
2024-01-05,ProductB,2500,25"""


@pytest.fixture
def sample_dataframe():
    """Sample pandas DataFrame for testing."""
    return pd.DataFrame({
        'Date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
        'Product': ['ProductA', 'ProductB', 'ProductA', 'ProductC', 'ProductB'],
        'Sales': [1000, 2000, 1500, 3000, 2500],
        'Quantity': [10, 20, 15, 30, 25]
    })


@pytest.fixture
def sample_file_id(sample_dataframe):
    """Store a sample dataframe and return its file ID."""
    file_id = "test_file_123"
    file_storage.save(
        file_id=file_id,
        filename="test.csv",
        uploaded_at="2024-01-01T00:00:00",
        metadata={"row_count": 5, "column_count": 4},
        dataframe=sample_dataframe
    )
    yield file_id
    # Cleanup
    if file_storage.exists(file_id):
        file_storage.delete(file_id)


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing AI service."""
    return {
        "row_count": 5,
        "column_count": 4,
        "columns": [
            {
                "name": "Date",
                "type": "datetime64[ns]",
                "cardinality": 5,
                "missingness_pct": 0
            },
            {
                "name": "Product",
                "type": "object",
                "cardinality": 3,
                "missingness_pct": 0
            },
            {
                "name": "Sales",
                "type": "int64",
                "cardinality": 5,
                "missingness_pct": 0,
                "stats": {
                    "min": 1000,
                    "max": 3000,
                    "mean": 2000,
                    "median": 2000,
                    "std": 707.1,
                    "q25": 1500,
                    "q75": 2500
                }
            },
            {
                "name": "Quantity",
                "type": "int64",
                "cardinality": 5,
                "missingness_pct": 0,
                "stats": {
                    "min": 10,
                    "max": 30,
                    "mean": 20,
                    "median": 20,
                    "std": 7.1,
                    "q25": 15,
                    "q75": 25
                }
            }
        ],
        "sample_data": [
            {"Date": "2024-01-01", "Product": "ProductA", "Sales": 1000, "Quantity": 10},
            {"Date": "2024-01-02", "Product": "ProductB", "Sales": 2000, "Quantity": 20},
            {"Date": "2024-01-03", "Product": "ProductA", "Sales": 1500, "Quantity": 15}
        ]
    }
