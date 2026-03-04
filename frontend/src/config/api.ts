/**
 * API Configuration
 * Centralizes API URL and related settings
 */
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  endpoints: {
    upload: '/api/upload',
    analyze: '/api/analyze',
    chartData: '/api/chart-data',
  },
} as const;

/**
 * Helper to build full API URLs
 */
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}${endpoint}`;
};
