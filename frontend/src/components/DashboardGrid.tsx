import { X, Maximize2, Minimize2 } from "lucide-react"
import { useState, useEffect } from "react"
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardAction } from "@/components/ui/card"
import type { UISuggestion, ChartDataResponse } from "@/types"
import { cn } from "@/lib/utils"
import { API_CONFIG, getApiUrl } from "@/config/api"

interface DashboardGridProps {
  suggestions: UISuggestion[]
  fileId: string
  onRemove: (id: string) => void
}

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
]

// Helper to format dates (remove time portion from ISO strings)
const formatDateValue = (value: unknown): string => {
  if (typeof value === 'string' && value.includes('T')) {
    // If it's an ISO date string, extract just the date part
    return value.split('T')[0]
  }
  return String(value)
}

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{ value: number; name: string; dataKey: string }>
  label?: string
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 shadow-lg">
      <p className="text-xs font-medium text-foreground mb-1">{formatDateValue(label)}</p>
      {payload.map((entry, i) => (
        <p key={i} className="text-xs text-muted-foreground">
          {entry.name}: <span className="font-mono text-foreground">{entry.value.toLocaleString()}</span>
        </p>
      ))}
    </div>
  )
}

interface ChartRendererProps {
  suggestion: UISuggestion
  fileId: string
}

function ChartRenderer({ suggestion, fileId }: ChartRendererProps) {
  const [data, setData] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(getApiUrl(API_CONFIG.endpoints.chartData), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            file_id: fileId,
            chart_type: suggestion.chartType,
            x_axis: suggestion.parameters.x_axis,
            y_axis: suggestion.parameters.y_axis,
            aggregation: suggestion.parameters.aggregation || "none",
          }),
        })

        if (!response.ok) {
          throw new Error("Error fetching chart data")
        }

        const chartData: ChartDataResponse = await response.json()
        setData(chartData.data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error loading chart")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [suggestion, fileId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-sm text-muted-foreground">Cargando datos...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-sm text-destructive">{error}</div>
      </div>
    )
  }

  const xKey = suggestion.parameters.x_axis || "name"
  const yKey = suggestion.parameters.y_axis || "value"

  switch (suggestion.chartType) {
    case "bar":
      return (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey={xKey}
              tick={{ fontSize: 11 }}
              className="text-muted-foreground"
              axisLine={false}
              tickLine={false}
              tickFormatter={formatDateValue}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              className="text-muted-foreground"
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey={yKey} radius={[4, 4, 0, 0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )
    case "line":
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey={xKey}
              tick={{ fontSize: 11 }}
              className="text-muted-foreground"
              axisLine={false}
              tickLine={false}
              tickFormatter={formatDateValue}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              className="text-muted-foreground"
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey={yKey}
              stroke={COLORS[0]}
              strokeWidth={2}
              dot={{ fill: COLORS[0], r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )
    case "pie":
      return (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="bottom"
              iconSize={8}
              formatter={(value: string) => (
                <span className="text-xs text-muted-foreground">{value}</span>
              )}
            />
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="45%"
              outerRadius="70%"
              innerRadius="40%"
              paddingAngle={3}
              strokeWidth={0}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      )
    case "scatter":
      return (
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey={xKey}
              tick={{ fontSize: 11 }}
              className="text-muted-foreground"
              axisLine={false}
              tickLine={false}
              type="number"
            />
            <YAxis
              dataKey={yKey}
              tick={{ fontSize: 11 }}
              className="text-muted-foreground"
              axisLine={false}
              tickLine={false}
              type="number"
            />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={data} fill={COLORS[0]} />
          </ScatterChart>
        </ResponsiveContainer>
      )
  }
}

export function DashboardGrid({ suggestions, fileId, onRemove }: DashboardGridProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  if (suggestions.length === 0) {
    return null
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">Tu Dashboard</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {suggestions.length} {suggestions.length === 1 ? "visualizacion" : "visualizaciones"} activas
          </p>
        </div>
      </div>

      <div className={cn(
        "grid gap-4",
        expandedId
          ? "grid-cols-1"
          : suggestions.length === 1
          ? "grid-cols-1"
          : "grid-cols-1 md:grid-cols-2"
      )}>
        {suggestions.map((suggestion, index) => {
          const isExpanded = expandedId === suggestion.id
          if (expandedId && !isExpanded) return null

          return (
            <Card
              key={suggestion.id}
              className={cn(
                "overflow-hidden animate-in fade-in slide-in-from-bottom-2 transition-all duration-300",
                isExpanded ? "col-span-full" : ""
              )}
              style={{ animationDelay: `${index * 80}ms`, animationFillMode: "backwards" }}
            >
              <CardHeader className="pb-0">
                <CardTitle className="text-sm">{suggestion.title}</CardTitle>
                <CardAction>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : suggestion.id)}
                      className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
                      aria-label={isExpanded ? "Contraer" : "Expandir"}
                    >
                      {isExpanded ? (
                        <Minimize2 className="h-3.5 w-3.5" />
                      ) : (
                        <Maximize2 className="h-3.5 w-3.5" />
                      )}
                    </button>
                    <button
                      onClick={() => onRemove(suggestion.id)}
                      className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                      aria-label="Eliminar del dashboard"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </CardAction>
              </CardHeader>
              <CardContent>
                <div className={cn("w-full", isExpanded ? "h-[500px]" : "h-[280px]")}>
                  <ChartRenderer suggestion={suggestion} fileId={fileId} />
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
