import { describe, it, expect } from 'vitest'
import { API_CONFIG, getApiUrl } from '../config/api'

describe('API Configuration', () => {
  it('should have all required endpoints', () => {
    expect(API_CONFIG.endpoints.upload).toBeDefined()
    expect(API_CONFIG.endpoints.analyze).toBeDefined()
    expect(API_CONFIG.endpoints.chartData).toBeDefined()
    expect(API_CONFIG.endpoints.query).toBeDefined()
  })

  it('should build correct API URL in development', () => {
    const url = getApiUrl('/api/test')
    expect(url).toContain('/api/test')
  })

  it('should build complete URLs with baseURL', () => {
    const uploadUrl = getApiUrl(API_CONFIG.endpoints.upload)
    expect(uploadUrl).toBe('http://localhost:8000/api/upload')
  })
})
