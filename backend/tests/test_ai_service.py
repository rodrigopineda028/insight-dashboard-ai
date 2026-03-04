"""Unit tests for AI service."""
import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService


@pytest.mark.unit
class TestAIService:
    """Test cases for AIService."""
    
    def test_build_analysis_prompt(self, sample_metadata):
        """Test analysis prompt generation."""
        service = AIService()
        prompt = service.build_analysis_prompt(sample_metadata)
        
        assert isinstance(prompt, str)
        assert 'Eres un analista de datos experto' in prompt
        assert 'Date' in prompt
        assert 'Product' in prompt
        assert 'Sales' in prompt
        assert 'bar' in prompt
        assert 'line' in prompt
        assert 'pie' in prompt
        assert 'scatter' in prompt
    
    @pytest.mark.asyncio
    async def test_analyze_dataset_validates_columns(self, sample_metadata):
        """Test that analyze_dataset validates column names."""
        service = AIService()
        
        # Mock Claude API response with invalid column
        mock_response = Mock()
        mock_response.content = [Mock(text='[{"title": "Test", "chart_type": "bar", "parameters": {"x_axis": "InvalidColumn", "y_axis": "Sales", "aggregation": "sum"}, "insight": "Test"}]')]
        
        with patch.object(service.client.messages, 'create', return_value=mock_response):
            with pytest.raises(Exception) as exc_info:
                await service.analyze_dataset(sample_metadata)
            
            assert 'InvalidColumn' in str(exc_info.value) or 'inválida' in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_analyze_dataset_validates_min_suggestions(self, sample_metadata):
        """Test that analyze_dataset requires 3-5 suggestions."""
        service = AIService()
        
        # Mock Claude API response with only 1 suggestion
        mock_response = Mock()
        mock_response.content = [Mock(text='[{"title": "Test", "chart_type": "bar", "parameters": {"x_axis": "Product", "y_axis": "Sales", "aggregation": "sum"}, "insight": "Test"}]')]
        
        with patch.object(service.client.messages, 'create', return_value=mock_response):
            with pytest.raises(Exception) as exc_info:
                await service.analyze_dataset(sample_metadata)
            
            assert '1 visualizaciones' in str(exc_info.value) or 'expected' in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_analyze_dataset_rejects_scatter_with_date(self, sample_metadata):
        """Test that scatter chart with date column is rejected."""
        service = AIService()
        
        # Mock Claude API response with 3 valid charts + 1 invalid scatter with date
        mock_response = Mock()
        mock_response.content = [Mock(text='[{"title": "Test1", "chart_type": "bar", "parameters": {"x_axis": "Product", "y_axis": "Sales", "aggregation": "sum"}, "insight": "Test"}, {"title": "Test2", "chart_type": "line", "parameters": {"x_axis": "Date", "y_axis": "Sales", "aggregation": "sum"}, "insight": "Test"}, {"title": "Test3", "chart_type": "scatter", "parameters": {"x_axis": "Date", "y_axis": "Sales", "aggregation": "none"}, "insight": "Test"}]')]
        
        with patch.object(service.client.messages, 'create', return_value=mock_response):
            with pytest.raises(Exception) as exc_info:
                await service.analyze_dataset(sample_metadata)
            
            error_msg = str(exc_info.value).lower()
            assert 'temporal' in error_msg or 'scatter' in error_msg or 'fecha' in error_msg
