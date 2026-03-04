"""Integration tests for API routes."""
import pytest
from io import BytesIO


@pytest.mark.integration
class TestUploadRoute:
    """Test cases for file upload endpoint."""
    
    def test_upload_csv_success(self, client, sample_csv_content):
        """Test successful CSV upload."""
        files = {
            'file': ('test.csv', BytesIO(sample_csv_content.encode()), 'text/csv')
        }
        response = client.post('/api/upload', files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data  # API returns 'id' not 'file_id'
        assert 'metadata' in data
        assert data['metadata']['row_count'] == 5
        assert data['metadata']['column_count'] == 4
    
    def test_upload_invalid_file(self, client):
        """Test upload with invalid file type."""
        files = {
            'file': ('test.txt', BytesIO(b'invalid content'), 'text/plain')
        }
        response = client.post('/api/upload', files=files)
        
        assert response.status_code == 400


@pytest.mark.integration
class TestChartDataRoute:
    """Test cases for chart data endpoint."""
    
    def test_get_chart_data_bar(self, client, sample_file_id):
        """Test getting bar chart data."""
        payload = {
            'file_id': sample_file_id,
            'chart_type': 'bar',
            'x_axis': 'Product',
            'y_axis': 'Sales',
            'aggregation': 'sum'
        }
        response = client.post('/api/chart-data', json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert len(data['data']) > 0
        assert data['chart_type'] == 'bar'
    
    def test_get_chart_data_invalid_column(self, client, sample_file_id):
        """Test with invalid column name."""
        payload = {
            'file_id': sample_file_id,
            'chart_type': 'bar',
            'x_axis': 'InvalidColumn',
            'y_axis': 'Sales',
            'aggregation': 'sum'
        }
        response = client.post('/api/chart-data', json=payload)
        
        assert response.status_code == 400
    
    def test_get_chart_data_file_not_found(self, client):
        """Test with non-existent file ID."""
        payload = {
            'file_id': 'nonexistent_file',
            'chart_type': 'bar',
            'x_axis': 'Product',
            'y_axis': 'Sales',
            'aggregation': 'sum'
        }
        response = client.post('/api/chart-data', json=payload)
        
        assert response.status_code == 404
