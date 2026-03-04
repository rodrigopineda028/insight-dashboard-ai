/**
 * Shared TypeScript types and interfaces
 */

// File upload and metadata types
export interface ColumnInfo {
  name: string;
  type: string;
  non_null_count: number;
  null_count: number;
  missingness_pct?: number;
  cardinality?: number;
  stats?: {
    min: number;
    max: number;
    mean: number;
    median: number;
    std?: number;
    q25?: number;
    q75?: number;
  };
}

export interface FileMetadata {
  row_count: number;
  column_count: number;
  columns: ColumnInfo[];
  sample_data: Record<string, unknown>[];
}

export interface UploadResponse {
  id: string;
  filename: string;
  uploaded_at: string;
  metadata: FileMetadata;
}

// Analysis and chart types (backend format)
export interface ChartParameters {
  x_axis?: string;
  y_axis?: string;
  aggregation?: 'sum' | 'count' | 'avg' | 'none';
}

export interface ChartSuggestion {
  title: string;
  chart_type: ChartType;
  parameters: ChartParameters;
  insight: string;
}

export interface AnalyzeResponse {
  file_id: string;
  suggestions: ChartSuggestion[];
  total_suggestions: number;
}

// Chart configuration
export type ChartType = 'bar' | 'line' | 'pie' | 'scatter';

export interface ChartConfig {
  id: string;
  title: string;
  chart_type: ChartType;
  x_axis: string;
  y_axis?: string;
  aggregation: 'sum' | 'count' | 'avg' | 'none';
}

export interface ChartData {
  id: string;
  data: Record<string, unknown>[];
  config: ChartConfig;
  loading: boolean;
  error: string | null;
}

// Chart data API response
export interface ChartDataResponse {
  chart_type: ChartType;
  x_axis: string;
  y_axis: string | null;
  data: Record<string, unknown>[];
  total_points: number;
}

// UI-specific types (for new component structure)
export interface UISuggestion {
  id: string;
  title: string;
  description: string;
  chartType: ChartType;
  insight: string;
  columns: string[];
  parameters: ChartParameters;
}

// Helper to convert backend ChartSuggestion to UI format
export function convertToUISuggestion(
  suggestion: ChartSuggestion,
  index: number
): UISuggestion {
  return {
    id: `chart-${index + 1}`,
    title: suggestion.title,
    description: suggestion.title, // Backend doesn't have separate description
    chartType: suggestion.chart_type,
    insight: suggestion.insight,
    columns: [
      suggestion.parameters.x_axis || '',
      suggestion.parameters.y_axis || ''
    ].filter(Boolean),
    parameters: suggestion.parameters
  };
}
