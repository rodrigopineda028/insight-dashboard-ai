import { useCallback, useEffect, useState } from 'react'

type HealthResponse = {
  status: string
  message: string
}

const apiUrl = `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/health`

function App() {
  const [message, setMessage] = useState<string>('')
  const [isOnline, setIsOnline] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(false)

  const checkBackend = useCallback(async () => {
    setLoading(true)
    setIsOnline(null)
    try {
      const response = await fetch(apiUrl)
      const data = (await response.json()) as HealthResponse
      setMessage(data.message)
      setIsOnline(true)
    } catch {
      setMessage('No se pudo conectar al backend')
      setIsOnline(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    checkBackend()
  }, [checkBackend])

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <div className="flex w-96 flex-col gap-6 rounded-2xl border border-slate-800 bg-slate-900 p-8">
        <h1 className="text-center text-2xl font-bold text-slate-100">Insight Dash AI</h1>
        
        <div className="flex items-center justify-center gap-3">
          <div className={`h-3 w-3 rounded-full ${
            loading ? 'animate-pulse bg-yellow-400' : 
            isOnline === true ? 'bg-emerald-400' : 
            isOnline === false ? 'bg-red-400' : 'bg-slate-600'
          }`} />
          <p className="text-sm text-slate-300">
            {loading ? 'Verificando...' : message || 'Sin estado'}
          </p>
        </div>

        <button
          onClick={checkBackend}
          disabled={loading}
          className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Consultando...' : 'Verificar conexión'}
        </button>
      </div>
    </div>
  )
}

export default App
