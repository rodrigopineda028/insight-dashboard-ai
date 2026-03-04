"""Unit tests for chart service."""
import pytest
import pandas as pd
from app.services.chart_service import ChartService


@pytest.mark.unit
class TestChartService:
    """Test cases for ChartService."""
    
    def test_aggregate_data_bar_chart(self, sample_dataframe):
        """Test aggregation for bar charts."""
        service = ChartService()
        result = service.aggregate_data(
            df=sample_dataframe,
            x_col='Product',
            y_col='Sales',
            agg_type='sum'
        )
        
        assert len(result) == 3  # 3 unique products
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        
        # Check aggregation worked correctly
        product_a = next(item for item in result if item['Product'] == 'ProductA')
        assert product_a['Sales'] == 2500  # 1000 + 1500
    
    def test_aggregate_data_with_avg(self, sample_dataframe):
        """Test average aggregation."""
        service = ChartService()
        result = service.aggregate_data(
            df=sample_dataframe,
            x_col='Product',
            y_col='Quantity',
            agg_type='avg'
        )
        
        product_b = next(item for item in result if item['Product'] == 'ProductB')
        assert product_b['Quantity'] == 22.5  # (20 + 25) / 2
    
    def test_aggregate_data_with_count(self, sample_dataframe):
        """Test count aggregation."""
        service = ChartService()
        result = service.aggregate_data(
            df=sample_dataframe,
            x_col='Product',
            y_col='Sales',
            agg_type='count'
        )
        
        product_a = next(item for item in result if item['Product'] == 'ProductA')
        assert product_a['count'] == 2  # ProductA appears twice
    
    def test_process_scatter_chart(self, sample_dataframe):
        """Test scatter chart processing."""
        service = ChartService()
        result = service.process_scatter_chart(
            df=sample_dataframe,
            x_col='Sales',
            y_col='Quantity'
        )
        
        assert len(result) == 5  # All rows should be included
        assert all('Sales' in row and 'Quantity' in row for row in result)
    
    def test_get_chart_data_bar(self, sample_dataframe):
        """Test complete chart data generation for bar chart."""
        service = ChartService()
        result = service.get_chart_data(
            df=sample_dataframe,
            chart_type='bar',
            x_axis='Product',
            y_axis='Sales',
            aggregation='sum'
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(item, dict) for item in result)
    
    def test_get_chart_data_pie(self, sample_dataframe):
        """Test pie chart data generation."""
        service = ChartService()
        result = service.get_chart_data(
            df=sample_dataframe,
            chart_type='pie',
            x_axis='Product',
            y_axis='Sales',
            aggregation='sum'
        )
        
        assert isinstance(result, list)
        # Pie chart should have 'name' and 'value' keys
        assert all('name' in item and 'value' in item for item in result)
