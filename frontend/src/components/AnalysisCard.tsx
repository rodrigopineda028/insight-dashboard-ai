import { Plus, Check, BarChart3, PieChart, LineChart, ScatterChart } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { UISuggestion } from "@/types"

interface AnalysisCardProps {
  suggestion: UISuggestion
  isAdded: boolean
  onToggle: (id: string) => void
  index: number
}

const chartIcons = {
  bar: BarChart3,
  line: LineChart,
  pie: PieChart,
  scatter: ScatterChart,
}

const chartLabels = {
  bar: "Barras",
  line: "Lineas",
  pie: "Circular",
  scatter: "Dispersión",
}

export function AnalysisCard({ suggestion, isAdded, onToggle, index }: AnalysisCardProps) {
  const Icon = chartIcons[suggestion.chartType]

  return (
    <Card
      className={cn(
        "relative overflow-hidden transition-all duration-300 animate-in fade-in slide-in-from-bottom-4 group",
        isAdded
          ? "border-primary/40 bg-primary/5"
          : "hover:border-primary/20 hover:bg-card/80"
      )}
      style={{ animationDelay: `${index * 100}ms`, animationFillMode: "backwards" }}
    >
      {isAdded && (
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-primary" />
      )}
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className={cn(
              "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg transition-colors",
              isAdded ? "bg-primary/20 text-primary" : "bg-secondary text-muted-foreground"
            )}>
              <Icon className="h-4.5 w-4.5" />
            </div>
            <div className="min-w-0">
              <CardTitle className="text-sm leading-snug text-balance">
                {suggestion.title}
              </CardTitle>
            </div>
          </div>
          <Badge variant="outline" className="shrink-0 text-xs font-mono">
            {chartLabels[suggestion.chartType]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <CardDescription className="text-sm leading-relaxed">
          {suggestion.description}
        </CardDescription>

        <div className="rounded-lg bg-secondary/50 border border-border/50 p-3">
          <p className="text-xs text-primary font-medium mb-1">Insight de IA</p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {suggestion.insight}
          </p>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {suggestion.columns.map((col) => (
            <span
              key={col}
              className="inline-flex items-center rounded-md bg-secondary px-2 py-0.5 text-xs font-mono text-muted-foreground"
            >
              {col}
            </span>
          ))}
        </div>

        <Button
          onClick={() => onToggle(suggestion.id)}
          variant={isAdded ? "secondary" : "default"}
          size="sm"
          className={cn(
            "w-full transition-all",
            isAdded ? "text-foreground" : ""
          )}
        >
          {isAdded ? (
            <>
              <Check className="h-4 w-4 mr-2" />
              Agregado al Dashboard
            </>
          ) : (
            <>
              <Plus className="h-4 w-4 mr-2" />
              Agregar al Dashboard
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}
