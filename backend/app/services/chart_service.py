"""Chart data processing service."""
from typing import Any, Dict, List

import pandas as pd

from app.config.settings import settings


class ChartService:
    """Service for processing and aggregating chart data."""
    
    @staticmethod
    def aggregate_data(df: pd.DataFrame, x_col: str, y_col: str | None, agg_type: str) -> List[Dict[str, Any]]:
        """Aggregate data based on chart parameters."""
        
        if agg_type == "count":
            # Count occurrences of each category
            result = df[x_col].value_counts().reset_index()
            result.columns = [x_col, "count"]
            return result.to_dict(orient="records")
        
        elif agg_type == "none" and y_col:
            # No aggregation, return as is (for scatter or line charts with direct values)
            result = df[[x_col, y_col]].dropna()
            return result.to_dict(orient="records")
        
        elif agg_type in ["sum", "avg"] and y_col:
            # Group by x_col and aggregate y_col
            grouped = df.groupby(x_col)[y_col]
            
            if agg_type == "sum":
                result = grouped.sum().reset_index()
            else:  # avg
                result = grouped.mean().reset_index()
            
            result.columns = [x_col, y_col]
            return result.to_dict(orient="records")
        
        else:
            # Default: just return unique values
            result = df[x_col].value_counts().reset_index()
            result.columns = [x_col, "value"]
            return result.to_dict(orient="records")
    
    @staticmethod
    def process_pie_chart(df: pd.DataFrame, column: str) -> List[Dict[str, Any]]:
        """Process data for pie chart (top N categories)."""
        counts = df[column].value_counts().head(settings.PIE_CHART_MAX_CATEGORIES)
        result = counts.reset_index()
        result.columns = ["name", "value"]
        return result.to_dict(orient="records")
    
    @staticmethod
    def process_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, agg_type: str) -> List[Dict[str, Any]]:
        """Process data for bar chart."""
        return ChartService.aggregate_data(df, x_col, y_col, agg_type)
    
    @staticmethod
    def process_line_chart(df: pd.DataFrame, x_col: str, y_col: str, agg_type: str) -> List[Dict[str, Any]]:
        """Process data for line chart (typically temporal data)."""
        data = ChartService.aggregate_data(df, x_col, y_col, agg_type)
        
        # Sort by x_axis (important for line charts to show trends)
        if data:
            try:
                # Try to sort as datetime if possible
                df_temp = pd.DataFrame(data)
                df_temp[x_col] = pd.to_datetime(df_temp[x_col], errors='ignore')
                data = df_temp.sort_values(x_col).to_dict(orient="records")
            except:
                # If not datetime, sort as is
                data = sorted(data, key=lambda x: x[x_col])
        
        return data
    
    @staticmethod
    def process_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str) -> List[Dict[str, Any]]:
        """Process data for scatter chart."""
        # For scatter, we want individual points, no aggregation
        # Limit to max points for performance
        result = df[[x_col, y_col]].dropna().head(settings.SCATTER_MAX_POINTS)
        return result.to_dict(orient="records")
    
    def get_chart_data(
        self,
        df: pd.DataFrame,
        chart_type: str,
        x_axis: str,
        y_axis: str | None,
        aggregation: str
    ) -> List[Dict[str, Any]]:
        """
        Get processed data for a specific chart type.
        
        Args:
            df: Source DataFrame
            chart_type: Type of chart (bar, line, pie, scatter)
            x_axis: Column name for x-axis
            y_axis: Column name for y-axis (optional for pie)
            aggregation: Aggregation type (sum, count, avg, none)
            
        Returns:
            List of data points ready for chart rendering
            
        Raises:
            ValueError: If chart type is invalid or required parameters missing
        """
        if chart_type == "pie":
            return self.process_pie_chart(df, x_axis)
        elif chart_type == "bar":
            if not y_axis:
                raise ValueError("Bar chart requires y_axis")
            return self.process_bar_chart(df, x_axis, y_axis, aggregation)
        elif chart_type == "line":
            if not y_axis:
                raise ValueError("Line chart requires y_axis")
            return self.process_line_chart(df, x_axis, y_axis, aggregation)
        elif chart_type == "scatter":
            if not y_axis:
                raise ValueError("Scatter chart requires y_axis")
            return self.process_scatter_chart(df, x_axis, y_axis)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")


# Singleton instance
chart_service = ChartService()
