"""Chart data processing service."""
from typing import Any, Dict, List

import pandas as pd

from app.config.settings import settings


class ChartService:
    """Service for processing and aggregating chart data."""
    
    @staticmethod
    def aggregate_data(df: pd.DataFrame, x_col: str, y_col: str | None, agg_type: str) -> List[Dict[str, Any]]:
        """Aggregate data based on chart parameters."""
        
        # Check if x_col is a date column and should be grouped by month
        df_copy = df.copy()
        is_date_column = False
        
        try:
            # Try to convert to datetime
            df_copy[x_col] = pd.to_datetime(df_copy[x_col])
            is_date_column = True
            
            # If it's a date and has more than 15 unique values (likely daily data)
            # group by month for better visualization
            unique_dates = df_copy[x_col].nunique()
            if unique_dates > 15:
                # Create a month column (e.g., "2024-01" format)
                df_copy['_month'] = df_copy[x_col].dt.to_period('M').astype(str)
                x_col_to_use = '_month'
            else:
                # Keep as dates but format nicely
                df_copy[x_col] = df_copy[x_col].dt.strftime('%Y-%m-%d')
                x_col_to_use = x_col
        except (ValueError, TypeError):
            # Not a date column, use as is
            x_col_to_use = x_col
        
        if agg_type == "count":
            # Count occurrences of each category
            result = df_copy[x_col_to_use].value_counts().reset_index()
            result.columns = [x_col, "count"]
            return result.to_dict(orient="records")
        
        elif agg_type == "none" and y_col:
            # No aggregation, return as is (for scatter or line charts with direct values)
            if is_date_column and x_col_to_use == x_col:
                # For dates without grouping, keep formatted dates
                result = df_copy[[x_col, y_col]].dropna()
            else:
                result = df[[x_col, y_col]].dropna()
            return result.to_dict(orient="records")
        
        elif agg_type in ["sum", "avg"] and y_col:
            # Group by x_col and aggregate y_col
            grouped = df_copy.groupby(x_col_to_use)[y_col]
            
            if agg_type == "sum":
                result = grouped.sum().reset_index()
            else:  # avg
                result = grouped.mean().reset_index()
            
            result.columns = [x_col, y_col]
            return result.to_dict(orient="records")
        
        else:
            # Default: just return unique values
            result = df_copy[x_col_to_use].value_counts().reset_index()
            result.columns = [x_col, "value"]
            return result.to_dict(orient="records")
    
    @staticmethod
    def process_pie_chart(df: pd.DataFrame, column: str, value_column: str | None = None) -> List[Dict[str, Any]]:
        """Process data for pie chart (top N categories)."""
        if value_column:
            # Aggregate values by category (e.g., sum of sales per region)
            grouped = df.groupby(column)[value_column].sum()
            result = grouped.nlargest(settings.PIE_CHART_MAX_CATEGORIES).reset_index()
            result.columns = ["name", "value"]
        else:
            # Just count occurrences
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
                # Try to convert to datetime, keep original if it fails
                try:
                    df_temp[x_col] = pd.to_datetime(df_temp[x_col])
                except (ValueError, TypeError):
                    pass  # Keep original values if conversion fails
                data = df_temp.sort_values(x_col).to_dict(orient="records")
            except Exception:
                # If not datetime, sort as is
                data = sorted(data, key=lambda x: x[x_col])
        
        return data
    
    @staticmethod
    def process_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str) -> List[Dict[str, Any]]:
        """Process data for scatter chart (numeric correlation only)."""
        # Scatter charts require numeric values on both axes
        df_copy = df[[x_col, y_col]].copy().dropna()
        
        # Ensure both columns are numeric (coerce non-numeric to NaN)
        df_copy[x_col] = pd.to_numeric(df_copy[x_col], errors='coerce')
        df_copy[y_col] = pd.to_numeric(df_copy[y_col], errors='coerce')
        
        # Drop rows where conversion to numeric failed
        df_copy = df_copy.dropna()
        
        # Limit to max points for performance
        result = df_copy.head(settings.SCATTER_MAX_POINTS)
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
            return self.process_pie_chart(df, x_axis, y_axis)
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
