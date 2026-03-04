import { useState, useEffect } from 'react';
import { BarChartComponent } from './charts/BarChartComponent';
import { LineChartComponent } from './charts/LineChartComponent';
import { PieChartComponent } from './charts/PieChartComponent';
import { ScatterChartComponent } from './charts/ScatterChartComponent';
import { ChartSkeleton, ErrorMessage, EmptyState } from './ui/FeedbackComponents';

const apiUrl = import.meta.env.VITE_API_URL;

interface ChartConfig {
  id: string;
  title: string;
  chart_type: 'bar' | 'line' | 'pie' | 'scatter';
  x_axis: string;
  y_axis?: string;
  aggregation: 'sum' | 'count' | 'avg' | 'none';
}

interface ChartData {
  id: string;
  data: any[];
  config: ChartConfig;
  loading: boolean;
  error: string | null;
}

interface DashboardProps {
  fileId: string;
  charts: ChartConfig[];
  onRemoveChart: (chartId: string) => void;
}

export function Dashboard({ fileId, charts, onRemoveChart }: DashboardProps) {
  const [chartsData, setChartsData] = useState<ChartData[]>([]);

  useEffect(() => {
    // Initialize charts data state
    setChartsData(
      charts.map(chart => ({
        id: chart.id,
        data: [],
        config: chart,
        loading: true,
        error: null,
      }))
    );

    // Fetch data for each chart
    charts.forEach(chart => {
      fetchChartData(chart);
    });
  }, [charts, fileId]);

  const fetchChartData = async (chart: ChartConfig) => {
    try {
      const response = await fetch(`${apiUrl}/api/chart-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_id: fileId,
          chart_type: chart.chart_type,
          x_axis: chart.x_axis,
          y_axis: chart.y_axis,
          aggregation: chart.aggregation,
        }),
      });

      if (!response.ok) {
        throw new Error('Error al obtener datos del gráfico');
      }

      const result = await response.json();

      setChartsData(prev =>
        prev.map(c =>
          c.id === chart.id
            ? { ...c, data: result.data, loading: false }
            : c
        )
      );
    } catch (error) {
      setChartsData(prev =>
        prev.map(c =>
          c.id === chart.id
            ? { ...c, loading: false, error: (error as Error).message }
            : c
        )
      );
    }
  };

  const renderChart = (chartData: ChartData) => {
    const { config, data, loading, error } = chartData;

    if (loading) {
      return <ChartSkeleton />;
    }

    if (error) {
      return (
        <ErrorMessage 
          message={error} 
          onRetry={() => fetchChartData(config)}
        />
      );
    }

    switch (config.chart_type) {
      case 'bar':
        return <BarChartComponent data={data} xKey={config.x_axis} yKey={config.y_axis!} title={config.title} />;
      case 'line':
        return <LineChartComponent data={data} xKey={config.x_axis} yKey={config.y_axis!} title={config.title} />;
      case 'pie':
        return <PieChartComponent data={data} title={config.title} />;
      case 'scatter':
        return <ScatterChartComponent data={data} xKey={config.x_axis} yKey={config.y_axis!} title={config.title} />;
      default:
        return null;
    }
  };

  if (charts.length === 0) {
    return (
      <EmptyState
        icon="📊"
        title="No hay gráficos en el dashboard"
        description="Analiza el archivo con AI y agrega visualizaciones desde las sugerencias para comenzar a explorar tus datos."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
        <p className="text-gray-600">{charts.length} gráfico(s)</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        {chartsData.map(chartData => (
          <div key={chartData.id} className="relative">
            <button
              onClick={() => onRemoveChart(chartData.id)}
              className="absolute top-2 right-2 z-10 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-600 transition-colors shadow-lg"
              title="Eliminar gráfico"
            >
              ✕
            </button>
            {renderChart(chartData)}
          </div>
        ))}
      </div>
    </div>
  );
}

