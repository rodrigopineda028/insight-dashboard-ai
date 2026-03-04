export function LoadingSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-8 bg-slate-800 rounded w-1/3"></div>
      <div className="h-64 bg-slate-800 rounded"></div>
      <div className="grid grid-cols-2 gap-4">
        <div className="h-32 bg-slate-800 rounded"></div>
        <div className="h-32 bg-slate-800 rounded"></div>
      </div>
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-2/3 mb-4"></div>
      <div className="h-[300px] bg-gray-100 rounded flex items-center justify-center">
        <div className="space-y-3 w-full px-8">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6"></div>
        </div>
      </div>
    </div>
  );
}

export function ErrorMessage({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-lg border border-red-800 bg-red-900/20 p-4">
      <div className="flex items-start gap-3">
        <span className="text-2xl">⚠️</span>
        <div className="flex-1">
          <h3 className="font-semibold text-red-300">Error</h3>
          <p className="mt-1 text-sm text-red-200">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 rounded bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 transition-colors"
            >
              Reintentar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export function EmptyState({ 
  icon, 
  title, 
  description, 
  action 
}: { 
  icon: string; 
  title: string; 
  description: string; 
  action?: { label: string; onClick: () => void } 
}) {
  return (
    <div className="text-center py-12">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-700 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6 max-w-md mx-auto">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
