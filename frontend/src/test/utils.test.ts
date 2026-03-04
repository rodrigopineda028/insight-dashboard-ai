import { describe, it, expect } from 'vitest'
import { formatDateValue } from '../utils/dateUtils'

describe('Date Utils', () => {
  it('should format ISO date string', () => {
    const result = formatDateValue('2024-01-15T00:00:00')
    expect(result).toBe('2024-01-15')
  })

  it('should handle regular date string', () => {
    const result = formatDateValue('2024-01-15')
    expect(result).toBe('2024-01-15')
  })

  it('should handle non-date values', () => {
    const result = formatDateValue('ProductA')
    expect(result).toBe('ProductA')
  })

  it('should handle numbers', () => {
    const result = formatDateValue(12345)
    expect(result).toBe('12345')
  })
})
