import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import AnalysisSuggestions from './AnalysisSuggestions'
import { Dashboard } from './Dashboard'

type FileMetadata = {
  row_count: number
  column_count: number
  columns: Array<{
    name: string
    type: string
    non_null_count: number
    null_count: number
    stats?: {
      min: number
      max: number
      mean: number
      median: number
    }
  }>
  sample_data: Record<string, unknown>[]
}

type UploadResponse = {
  id: string
  filename: string
  uploaded_at: string
  metadata: FileMetadata
}

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function FileUpload() {
  const [uploading, setUploading] = useState(false)
  const [fileData, setFileData] = useState<UploadResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [charts, setCharts] = useState<any[]>([])

  const handleAddChart = (suggestion: any) => {
    // Generate unique ID for each chart
    const chartWithId = {
      ...suggestion,
      id: `${suggestion.chart_type}-${Date.now()}-${Math.random()}`,
      x_axis: suggestion.parameters.x_axis,
      y_axis: suggestion.parameters.y_axis,
      aggregation: suggestion.parameters.aggregation || 'none',
    }
    setCharts((prev) => [...prev, chartWithId])
  }

  const handleRemoveChart = (chartId: string) => {
    setCharts((prev) => prev.filter((c) => c.id !== chartId))
  }

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setError(null)
    setFileData(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${apiUrl}/api/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error al subir archivo')
      }

      const data = (await response.json()) as UploadResponse
      setFileData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setUploading(false)
    }
  }, [])

  const onDropRejected = useCallback((fileRejections: any[]) => {
    const rejection = fileRejections[0]
    if (!rejection) return

    const { errors } = rejection
    const errorCode = errors[0]?.code

    let message = 'Error al procesar el archivo'
    
    if (errorCode === 'file-too-large') {
      message = 'Archivo muy grande. Máximo 5 MB'
    } else if (errorCode === 'file-invalid-type') {
      message = 'Formato no permitido. Use archivos CSV o XLSX'
    } else if (errorCode === 'too-many-files') {
      message = 'Solo puede subir un archivo a la vez'
    }

    setError(message)
    setFileData(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024, // 5 MB
  })

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6">
      <div className="w-full max-w-4xl space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-100">Insight Dash AI</h1>
          <p className="mt-2 text-slate-400">
            Sube tu archivo CSV o Excel para análisis instantáneo
          </p>
        </div>

        <div
          {...getRootProps()}
          className={`cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition ${
            isDragActive
              ? 'border-indigo-400 bg-indigo-500/10'
              : 'border-slate-700 bg-slate-900 hover:border-slate-600'
          }`}
        >
          <input {...getInputProps()} />
          
          {uploading ? (
            <div className="space-y-3">
              <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-slate-700 border-t-indigo-500" />
              <p className="text-slate-300">Procesando archivo...</p>
            </div>
          ) : isDragActive ? (
            <p className="text-lg text-indigo-300">Suelta el archivo aquí</p>
          ) : (
            <div className="space-y-2">
              <svg
                className="mx-auto h-12 w-12 text-slate-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="text-lg text-slate-300">
                Arrastra un archivo aquí o haz clic para seleccionar
              </p>
              <p className="text-sm text-slate-500">CSV o XLSX (máx. 5 MB)</p>
            </div>
          )}
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-center text-red-200">
            {error}
          </div>
        )}

        {fileData && (
          <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-slate-100">
                {fileData.filename}
              </h2>
              <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-sm text-emerald-300">
                ✓ Procesado
              </span>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl bg-slate-950/60 p-4">
                <p className="text-sm text-slate-400">Filas</p>
                <p className="text-2xl font-bold text-slate-100">
                  {fileData.metadata.row_count.toLocaleString()}
                </p>
              </div>
              <div className="rounded-xl bg-slate-950/60 p-4">
                <p className="text-sm text-slate-400">Columnas</p>
                <p className="text-2xl font-bold text-slate-100">
                  {fileData.metadata.column_count}
                </p>
              </div>
            </div>

            <div>
              <h3 className="mb-3 font-semibold text-slate-100">Columnas del dataset</h3>
              <div className="space-y-2">
                {fileData.metadata.columns.map((col) => (
                  <div
                    key={col.name}
                    className="flex items-center justify-between rounded-lg bg-slate-950/60 p-3 text-sm"
                  >
                    <span className="font-medium text-slate-200">{col.name}</span>
                    <div className="flex items-center gap-3">
                      <span className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-400">
                        {col.type}
                      </span>
                      {col.stats && (
                        <span className="text-xs text-slate-500">
                          min: {col.stats.min?.toFixed(1)} | max: {col.stats.max?.toFixed(1)}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="mb-3 font-semibold text-slate-100">Vista previa</h3>
              <div className="overflow-x-auto rounded-lg border border-slate-800">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-950/60">
                    <tr>
                      {fileData.metadata.columns.map((col) => (
                        <th key={col.name} className="px-4 py-2 font-medium text-slate-300">
                          {col.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {fileData.metadata.sample_data.map((row, idx) => (
                      <tr key={idx} className="border-t border-slate-800">
                        {fileData.metadata.columns.map((col) => (
                          <td key={col.name} className="px-4 py-2 text-slate-400">
                            {String(row[col.name] ?? '')}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <AnalysisSuggestions fileId={fileData.id} onAddChart={handleAddChart} />

            {charts.length > 0 && (
              <div className="mt-8">
                <Dashboard fileId={fileData.id} charts={charts} onRemoveChart={handleRemoveChart} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
