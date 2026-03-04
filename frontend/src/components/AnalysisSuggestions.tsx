import { useState } from 'react'

type ChartSuggestion = {
  title: string
  chart_type: string
  parameters: {
    x_axis?: string
    y_axis?: string
    aggregation?: string
  }
  insight: string
}

type AnalyzeResponse = {
  file_id: string
  suggestions: ChartSuggestion[]
  total_suggestions: number
}

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type Props = {
  fileId: string
  onAddChart: (suggestion: ChartSuggestion) => void
}

export default function AnalysisSuggestions({ fileId, onAddChart }: Props) {
  const [suggestions, setSuggestions] = useState<ChartSuggestion[]>([])
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analyzed, setAnalyzed] = useState(false)

  const analyzeFile = async () => {
    setAnalyzing(true)
    setError(null)

    try {
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_id: fileId }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error al analizar archivo')
      }

      const data = (await response.json()) as AnalyzeResponse
      setSuggestions(data.suggestions)
      setAnalyzed(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setAnalyzing(false)
    }
  }

  const getChartIcon = (type: string) => {
    switch (type) {
      case 'bar':
        return '📊'
      case 'line':
        return '📈'
      case 'pie':
        return '🍰'
      case 'scatter':
        return '⚡'
      default:
        return '📉'
    }
  }

  return (
    <div className="space-y-4">
      {!analyzed && (
        <div className="rounded-2xl border border-indigo-500/30 bg-indigo-500/10 p-6 text-center">
          <h3 className="mb-2 text-lg font-semibold text-slate-100">
            ✨ Análisis con IA
          </h3>
          <p className="mb-4 text-sm text-slate-300">
            Claude analizará tus datos y sugerirá las visualizaciones más impactantes
          </p>
          <button
            onClick={analyzeFile}
            disabled={analyzing}
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-2.5 font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Analizando con IA...
              </>
            ) : (
              'Analizar con Claude'
            )}
          </button>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-slate-100">
            Sugerencias de Claude ({suggestions.length})
          </h3>
          <div className="grid gap-4 md:grid-cols-2">
            {suggestions.map((suggestion, idx) => (
              <div
                key={idx}
                className="group rounded-2xl border border-slate-800 bg-slate-900/60 p-5 transition hover:border-slate-700"
              >
                <div className="mb-3 flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{getChartIcon(suggestion.chart_type)}</span>
                    <div>
                      <h4 className="font-semibold text-slate-100">{suggestion.title}</h4>
                      <span className="text-xs text-slate-500">
                        {suggestion.chart_type.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>

                <p className="mb-4 text-sm text-slate-300">{suggestion.insight}</p>

                {suggestion.parameters.x_axis && (
                  <div className="mb-4 flex flex-wrap gap-2 text-xs">
                    {suggestion.parameters.x_axis && (
                      <span className="rounded bg-slate-800 px-2 py-1 text-slate-400">
                        X: {suggestion.parameters.x_axis}
                      </span>
                    )}
                    {suggestion.parameters.y_axis && (
                      <span className="rounded bg-slate-800 px-2 py-1 text-slate-400">
                        Y: {suggestion.parameters.y_axis}
                      </span>
                    )}
                    {suggestion.parameters.aggregation && (
                      <span className="rounded bg-indigo-500/20 px-2 py-1 text-indigo-300">
                        {suggestion.parameters.aggregation}
                      </span>
                    )}
                  </div>
                )}

                <button
                  onClick={() => onAddChart(suggestion)}
                  className="w-full rounded-lg border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20"
                >
                  Agregar al Dashboard
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
