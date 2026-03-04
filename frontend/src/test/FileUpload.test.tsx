import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { FileUpload } from '../components/FileUpload'

describe('FileUpload Component', () => {
  it('renders upload area', () => {
    const mockOnFileUploaded = vi.fn()
    const mockOnError = vi.fn()
    render(<FileUpload onFileUploaded={mockOnFileUploaded} onError={mockOnError} />)
    
    expect(screen.getByText(/arrastra y suelta/i)).toBeInTheDocument()
  })

  it('displays supported file types', () => {
    const mockOnFileUploaded = vi.fn()
    const mockOnError = vi.fn()
    render(<FileUpload onFileUploaded={mockOnFileUploaded} onError={mockOnError} />)
    
    expect(screen.getByText('.csv')).toBeInTheDocument()
    expect(screen.getByText('.xlsx')).toBeInTheDocument()
  })

  it('shows upload prompt text', () => {
    const mockOnFileUploaded = vi.fn()
    const mockOnError = vi.fn()
    render(<FileUpload onFileUploaded={mockOnFileUploaded} onError={mockOnError} />)
    
    expect(screen.getByText(/busca en tu computador/i)).toBeInTheDocument()
  })
})
