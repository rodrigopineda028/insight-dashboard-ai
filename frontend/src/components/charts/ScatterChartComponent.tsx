import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ScatterChartProps {
  data: any[];
  xKey: string;
  yKey: string;
  title: string;
}

export function ScatterChartComponent({ data, xKey, yKey, title }: ScatterChartProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} name={xKey} />
          <YAxis dataKey={yKey} name={yKey} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter name={title} data={data} fill="#8b5cf6" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
