import { useCallback, useState } from "react"
import { Upload, FileSpreadsheet, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { API_CONFIG, getApiUrl } from "@/config/api"
import type { UploadResponse } from "@/types"

interface FileUploadProps {
  onFileUploaded: (response: UploadResponse) => void
  onError: (error: string) => void
}

export function FileUpload({ onFileUploaded, onError }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true)
    }
  }, [])

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const validateFile = (file: File): boolean => {
    const validTypes = [
      "text/csv",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "application/vnd.ms-excel",
    ]
    const validExtensions = [".csv", ".xlsx", ".xls"]
    const hasValidExtension = validExtensions.some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    )
    return validTypes.includes(file.type) || hasValidExtension
  }

  const uploadFile = async (file: File) => {
    setIsUploading(true)
    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch(getApiUrl(API_CONFIG.endpoints.upload), {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Error uploading file")
      }

      const data: UploadResponse = await response.json()
      onFileUploaded(data)
    } catch (error) {
      onError(error instanceof Error ? error.message : "Error uploading file")
      setSelectedFile(null)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0]
        if (validateFile(file)) {
          setSelectedFile(file)
          uploadFile(file)
        } else {
          onError("Formato de archivo no soportado. Usa CSV o XLSX.")
        }
      }
    },
    [onError]
  )

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        const file = e.target.files[0]
        if (validateFile(file)) {
          setSelectedFile(file)
          uploadFile(file)
        } else {
          onError("Formato de archivo no soportado. Usa CSV o XLSX.")
        }
      }
    },
    [onError]
  )

  const removeFile = useCallback(() => {
    setSelectedFile(null)
  }, [])

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
    return (bytes / (1024 * 1024)).toFixed(1) + " MB"
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!selectedFile ? (
        <label
          htmlFor="file-upload-input"
          className={cn(
            "relative flex flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed p-12 transition-all duration-300 cursor-pointer group",
            isDragging
              ? "border-primary bg-primary/5 scale-[1.02]"
              : "border-border hover:border-primary/50 hover:bg-secondary/50",
            isUploading && "opacity-50 pointer-events-none"
          )}
          onDragEnter={handleDragIn}
          onDragLeave={handleDragOut}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div
            className={cn(
              "flex h-16 w-16 items-center justify-center rounded-2xl transition-all duration-300",
              isDragging
                ? "bg-primary/20 text-primary"
                : "bg-secondary text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary"
            )}
          >
            <Upload className="h-7 w-7" strokeWidth={1.5} />
          </div>

          <div className="flex flex-col items-center gap-2 text-center">
            <p className="text-lg font-medium text-foreground">
              {isDragging ? "Suelta tu archivo aqui" : isUploading ? "Subiendo..." : "Arrastra y suelta tu archivo"}
            </p>
            <p className="text-sm text-muted-foreground">
              {"o "}
              <span className="text-primary font-medium underline underline-offset-4 decoration-primary/40">
                busca en tu computador
              </span>
            </p>
          </div>

          <div className="flex items-center gap-3 mt-2">
            <span className="inline-flex items-center gap-1.5 rounded-md bg-secondary px-3 py-1.5 text-xs font-mono text-muted-foreground">
              <FileSpreadsheet className="h-3.5 w-3.5" />
              .xlsx
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-md bg-secondary px-3 py-1.5 text-xs font-mono text-muted-foreground">
              <FileSpreadsheet className="h-3.5 w-3.5" />
              .csv
            </span>
          </div>

          <input
            id="file-upload-input"
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileInput}
            className="sr-only"
            disabled={isUploading}
          />
        </label>
      ) : (
        <div className="flex items-center gap-4 rounded-xl border border-border bg-card p-5 animate-in fade-in slide-in-from-bottom-2 duration-300">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10">
            <FileSpreadsheet className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">
              {selectedFile.name}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {isUploading ? "Subiendo..." : formatFileSize(selectedFile.size)}
            </p>
          </div>
          {!isUploading && (
            <button
              onClick={removeFile}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
              aria-label="Eliminar archivo"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      )}
    </div>
  )
}
