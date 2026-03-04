import { useState, useCallback, useRef } from "react"
import { FileUpload } from "@/components/FileUpload"
import { AnalysisLoader } from "@/components/AnalysisLoader"
import { AnalysisCard } from "@/components/AnalysisCard"
import { DashboardGrid } from "@/components/DashboardGrid"
import { Header } from "@/components/Header"
import { ArrowDown, LayoutDashboard, Lightbulb, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { UploadResponse, AnalyzeResponse, UISuggestion } from "@/types"
import { API_CONFIG, getApiUrl } from "@/config/api"

type AppState = "upload" | "analyzing" | "results"

export default function App() {
  const [appState, setAppState] = useState<AppState>("upload")
  const [fileId, setFileId] = useState<string>("")
  const [suggestions, setSuggestions] = useState<UISuggestion[]>([])
  const [dashboardItems, setDashboardItems] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const dashboardRef = useRef<HTMLDivElement>(null)

  const handleFileUploaded = useCallback((response: UploadResponse) => {
    setFileId(response.id)
    setAppState("analyzing")
    setAnalysisComplete(false)
    analyzeFile(response.id)
  }, [])

  const analyzeFile = async (id: string) => {
    try {
      const response = await fetch(getApiUrl(API_CONFIG.endpoints.analyze), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ file_id: id }),
      })

      if (!response.ok) {
        throw new Error("Error analyzing file")
      }

      const data: AnalyzeResponse = await response.json()
      
      // Convert backend suggestions to UI format
      const uiSuggestions: UISuggestion[] = data.suggestions.map((s, i) => ({
        id: `chart-${i + 1}`,
        title: s.title,
        description: s.title,
        chartType: s.chart_type,
        insight: s.insight,
        columns: [s.parameters.x_axis, s.parameters.y_axis].filter((c): c is string => !!c),
        parameters: s.parameters
      }))

      setSuggestions(uiSuggestions)
      setAnalysisComplete(true)
      
      // Wait briefly for smooth transition
      setTimeout(() => {
        setAppState("results")
      }, 300)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error analyzing file")
      setAppState("upload")
    }
  }

  const toggleDashboardItem = useCallback((id: string) => {
    setDashboardItems((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }, [])

  const removeDashboardItem = useCallback((id: string) => {
    setDashboardItems((prev) => prev.filter((i) => i !== id))
  }, [])

  const handleReset = useCallback(() => {
    setAppState("upload")
    setDashboardItems([])
    setSuggestions([])
    setFileId("")
    setError(null)
    setAnalysisComplete(false)
  }, [])

  const scrollToDashboard = useCallback(() => {
    dashboardRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  const handleUploadError = useCallback((errorMsg: string) => {
    setError(errorMsg)
  }, [])

  const activeSuggestions = suggestions.filter((s) => dashboardItems.includes(s.id))

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="mx-auto max-w-7xl px-6 py-10">
        {/* Upload State */}
        {appState === "upload" && (
          <div className="flex flex-col items-center gap-10 animate-in fade-in duration-500">
            <div className="flex flex-col items-center gap-4 text-center max-w-xl">
              <Badge variant="outline" className="font-mono text-xs">
                Potenciado por IA
              </Badge>
              <h1 className="text-3xl font-bold tracking-tight text-foreground text-balance sm:text-4xl">
                Convierte tus datos en insights accionables
              </h1>
              <p className="text-base text-muted-foreground leading-relaxed text-pretty">
                Sube tu hoja de calculo y nuestra IA analizara tus datos, sugerira
                visualizaciones y te ayudara a construir un dashboard en segundos.
              </p>
            </div>

            <FileUpload onFileUploaded={handleFileUploaded} onError={handleUploadError} />

            {error && (
              <div className="text-sm text-destructive bg-destructive/10 px-4 py-2 rounded-lg">
                {error}
              </div>
            )}

            <div className="flex items-center gap-6 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-accent" />
                <span>Analisis automatico</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                <span>Graficos inteligentes</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-chart-3" />
                <span>Dashboard en segundos</span>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {appState === "analyzing" && (
          <div className="flex items-center justify-center min-h-[60vh] animate-in fade-in duration-500">
            <AnalysisLoader isComplete={analysisComplete} />
          </div>
        )}

        {/* Results State */}
        {appState === "results" && (
          <div className="space-y-12 animate-in fade-in duration-500">
            {/* Results header */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-primary" />
                  Sugerencias de la IA
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Selecciona las visualizaciones que deseas agregar a tu dashboard
                </p>
              </div>
              <div className="flex items-center gap-2">
                {dashboardItems.length > 0 && (
                  <Button
                    variant="default"
                    size="sm"
                    onClick={scrollToDashboard}
                    className="gap-2"
                  >
                    <LayoutDashboard className="h-4 w-4" />
                    Ver Dashboard
                    <Badge variant="secondary" className="ml-1 bg-primary-foreground/20 text-primary-foreground text-xs">
                      {dashboardItems.length}
                    </Badge>
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleReset}
                  className="gap-2"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  Nuevo analisis
                </Button>
              </div>
            </div>

            {/* Analysis Cards Grid */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {suggestions.map((suggestion, index) => (
                <AnalysisCard
                  key={suggestion.id}
                  suggestion={suggestion}
                  isAdded={dashboardItems.includes(suggestion.id)}
                  onToggle={toggleDashboardItem}
                  index={index}
                />
              ))}
            </div>

            {/* Scroll indicator when dashboard has items */}
            {dashboardItems.length > 0 && (
              <div className="flex justify-center">
                <button
                  onClick={scrollToDashboard}
                  className="flex flex-col items-center gap-2 text-muted-foreground hover:text-primary transition-colors group"
                >
                  <span className="text-xs">Scroll al dashboard</span>
                  <ArrowDown className="h-4 w-4 animate-bounce" />
                </button>
              </div>
            )}

            {/* Dashboard Section */}
            <div ref={dashboardRef}>
              <DashboardGrid
                suggestions={activeSuggestions}
                fileId={fileId}
                onRemove={removeDashboardItem}
              />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 mt-20">
        <div className="mx-auto max-w-7xl px-6 py-6 flex items-center justify-between">
          <p className="text-xs text-muted-foreground">
            Insight AI - Analisis de datos inteligente
          </p>
        </div>
      </footer>
    </div>
  )
}
