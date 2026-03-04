import { useEffect, useState } from "react"
import { Brain, Table, BarChart3, Sparkles } from "lucide-react"

const steps = [
  { icon: Table, label: "Leyendo estructura de datos...", delay: 0 },
  { icon: Brain, label: "IA analizando patrones...", delay: 2000 },
  { icon: BarChart3, label: "Generando sugerencias...", delay: 4500 },
  { icon: Sparkles, label: "Finalizando análisis...", delay: 7000 },
]

interface AnalysisLoaderProps {
  isComplete?: boolean
}

export function AnalysisLoader({ isComplete = false }: AnalysisLoaderProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const stepTimers = steps.map((_, index) =>
      setTimeout(() => {
        setCurrentStep(index)
      }, steps[index].delay)
    )

    return () => {
      stepTimers.forEach(clearTimeout)
    }
  }, [])

  useEffect(() => {
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95 && !isComplete) {
          // Slow down near completion if backend hasn't responded
          return prev + 0.05
        }
        if (prev >= 100) {
          clearInterval(progressInterval)
          return 100
        }
        return prev + 0.8
      })
    }, 80)

    return () => {
      clearInterval(progressInterval)
    }
  }, [isComplete])

  // Auto-complete progress when backend responds
  useEffect(() => {
    if (isComplete) {
      setProgress(100)
    }
  }, [isComplete])

  return (
    <div className="w-full max-w-lg mx-auto flex flex-col items-center gap-8 py-12">
      {/* Animated orb */}
      <div className="relative flex h-28 w-28 items-center justify-center">
        <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" style={{ animationDuration: "2s" }} />
        <div className="absolute inset-2 rounded-full bg-primary/10 animate-pulse" />
        <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-card border border-border">
          <Brain className="h-9 w-9 text-primary animate-pulse" />
        </div>
      </div>

      {/* Steps */}
      <div className="flex flex-col items-center gap-6 w-full">
        <div className="flex flex-col gap-3 w-full">
          {steps.map((step, index) => {
            const Icon = step.icon
            const isActive = index === currentStep
            const isDone = index < currentStep

            return (
              <div
                key={index}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-500 ${
                  isActive
                    ? "bg-primary/10 border border-primary/20"
                    : isDone
                    ? "opacity-50"
                    : "opacity-20"
                }`}
              >
                <Icon
                  className={`h-4 w-4 shrink-0 transition-colors duration-300 ${
                    isActive ? "text-primary" : "text-muted-foreground"
                  }`}
                />
                <span
                  className={`text-sm transition-colors duration-300 ${
                    isActive ? "text-foreground font-medium" : "text-muted-foreground"
                  }`}
                >
                  {step.label}
                </span>
                {isActive && (
                  <div className="ml-auto flex gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Progress bar */}
        <div className="w-full bg-secondary rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-primary h-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  )
}
