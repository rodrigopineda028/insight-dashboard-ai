import { useState } from "react"
import { Send, Loader2, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { API_CONFIG, getApiUrl } from "@/config/api"
import type { ChartSuggestion } from "@/types"

interface ChatQueryProps {
  fileId: string
  onNewChart: (suggestion: ChartSuggestion) => void
}

export function ChatQuery({ fileId, onNewChart }: ChatQueryProps) {
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(getApiUrl(API_CONFIG.endpoints.query), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          file_id: fileId,
          query: query.trim(),
        }),
      })

      if (!response.ok) {
        throw new Error("Error processing query")
      }

      const data = await response.json()
      
      if (data.suggestion) {
        onNewChart(data.suggestion)
        setQuery("")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error processing query")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <Sparkles className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder='Ej: "Muestra ventas por mes" o "Compara categorías"'
                  className="flex-1 rounded-lg border border-input bg-background px-4 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={loading}
                />
                <Button type="submit" size="sm" disabled={loading || !query.trim()}>
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {error && (
                <p className="text-xs text-destructive">{error}</p>
              )}
              <p className="text-xs text-muted-foreground">
                Pregunta a la IA sobre tus datos para generar nuevas visualizaciones
              </p>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
