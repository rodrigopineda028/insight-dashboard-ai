/**
 * Formats date values by removing timestamp portion from ISO strings
 */
export const formatDateValue = (value: unknown): string => {
  if (typeof value === 'string' && value.includes('T')) {
    return value.split('T')[0]
  }
  return String(value)
}
