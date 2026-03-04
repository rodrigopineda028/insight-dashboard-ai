import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BarChartProps {
  data: any[];
  xKey: string;
  yKey: string;
  title: string;
}

export function BarChartComponent({ data, xKey, yKey, title }: BarChartProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} angle={-45} textAnchor="end" height={100} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={yKey} fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
