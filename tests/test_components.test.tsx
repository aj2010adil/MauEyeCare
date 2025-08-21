import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '../AuthContext'

// Mock components
import PrescriptionTable from '../components/prescriptions/PrescriptionTable'
import PrescriptionModal from '../components/prescriptions/PrescriptionModal'
import PrescriptionCard from '../components/prescriptions/PrescriptionCard'
import PrescriptionExporter from '../components/prescriptions/PrescriptionExporter'
import QRCodeStamp from '../components/prescriptions/QRCodeStamp'
import AutoSuggestInput from '../components/ui/AutoSuggestInput'
import SpectacleShowcase from '../components/spectacles/SpectacleShowcase'
import SpectacleCompare from '../components/spectacles/SpectacleCompare'
import TryOn3DViewer from '../components/spectacles/TryOn3DViewer'
import InventoryUploader from '../components/inventory/InventoryUploader'
import ImageEntryForm from '../components/inventory/ImageEntryForm'

// Mock data
const mockPatient = {
  id: 1,
  first_name: 'John',
  last_name: 'Doe',
  phone: '1234567890',
}

const mockPrescription = {
  id: 1,
  created_at: '2024-01-01T00:00:00Z',
  patient_id: 1,
  visit_id: 1,
  rx_values: {
    od_sphere: -2.5,
    od_cylinder: -0.5,
    od_axis: 90,
    os_sphere: -2.25,
    os_cylinder: -0.25,
    os_axis: 85
  },
  spectacles: [
    {
      name: 'Ray-Ban Aviator Classic',
      price: 8500.0,
      quantity: 1
    }
  ],
  medicines: {
    artificial_tears: {
      name: 'Artificial Tears',
      dosage: '1-2 drops as needed',
      quantity: 1,
      price: 150.0
    }
  },
  totals: {
    total: 8650.0
  },
  patient: mockPatient
}

const mockSpectacle = {
  id: 1,
  name: 'Ray-Ban Aviator Classic',
  brand: 'Ray-Ban',
  price: 8500.0,
  image_url: '/uploads/rayban-aviator.jpg',
  frame_material: 'Metal',
  frame_shape: 'Aviator',
  lens_type: 'Polarized',
  gender: 'Unisex',
  age_group: 'Adult',
  description: 'Classic aviator sunglasses',
  specifications: {
    lens_width: '58mm',
    bridge_width: '18mm',
    temple_length: '135mm'
  },
  quantity: 10,
  in_stock: true
}

// Mock fetch
global.fetch = vi.fn()

// Wrapper component for testing
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
      <Toaster />
    </AuthProvider>
  </BrowserRouter>
)

describe('PrescriptionTable', () => {
  it('renders prescription table correctly', () => {
    render(
      <TestWrapper>
        <PrescriptionTable 
          prescriptions={[mockPrescription]} 
          onDownload={vi.fn()} 
          sortBy="date" 
          sortOrder="desc" 
        />
      </TestWrapper>
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Complete')).toBeInTheDocument()
    expect(screen.getByText(/1\s+Spectacle\(s\)/)).toBeInTheDocument()
  })
})

describe('PrescriptionCard', () => {
  it('renders prescription card correctly', () => {
    render(
      <TestWrapper>
        <PrescriptionCard prescription={mockPrescription as any} onDownload={vi.fn()} />
      </TestWrapper>
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Complete')).toBeInTheDocument()
  })
})

describe('PrescriptionModal', () => {
  const mockProps = {
    isOpen: true,
    onClose: vi.fn(),
    onSuccess: vi.fn()
  }

  beforeEach(() => {
    // Mock patients and visits fetch
    ;(fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ([mockPatient])
    })
  })

  it('renders modal when open', async () => {
    render(
      <TestWrapper>
        <PrescriptionModal {...mockProps} />
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText('Create New Prescription')).toBeInTheDocument()
      expect(screen.getByText('Patient')).toBeInTheDocument()
      expect(screen.getByText('Visit (Optional)')).toBeInTheDocument()
    })
  })

  it('calls onClose when Cancel is clicked', async () => {
    render(
      <TestWrapper>
        <PrescriptionModal {...mockProps} />
      </TestWrapper>
    )

    await waitFor(() => {
      const cancelBtn = screen.getByText('Cancel')
      fireEvent.click(cancelBtn)
      expect(mockProps.onClose).toHaveBeenCalled()
    })
  })
})

describe('PrescriptionExporter', () => {
  const mockProps = {
    prescription: mockPrescription as any,
    patient: mockPatient,
    onClose: vi.fn()
  }

  it('renders export options', () => {
    render(
      <TestWrapper>
        <PrescriptionExporter {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('Export Prescription')).toBeInTheDocument()
  })
})

describe('QRCodeStamp', () => {
  it('renders QR code modal', () => {
    render(
      <TestWrapper>
        <QRCodeStamp prescriptionId={1} patientName="John Doe" onClose={vi.fn()} />
      </TestWrapper>
    )

    expect(screen.getByText('QR Code')).toBeInTheDocument()
    expect(screen.getByText('Download QR Code')).toBeInTheDocument()
    expect(screen.getByText('Copy URL')).toBeInTheDocument()
  })
})

describe('AutoSuggestInput', () => {
  const mockSuggestions = [
    { id: 1, label: 'John Doe', value: 'John Doe', description: 'Patient' },
    { id: 2, label: 'Jane Smith', value: 'Jane Smith', description: 'Patient' }
  ]

  it('renders input field', () => {
    render(
      <TestWrapper>
        <AutoSuggestInput 
          value="" 
          onChange={vi.fn()} 
          suggestions={mockSuggestions as any} 
          label="Patient Name" 
          placeholder="Search patients..." 
        />
      </TestWrapper>
    )

    expect(screen.getByText('Patient Name')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Search patients...')).toBeInTheDocument()
  })

  it('shows suggestions when typing', async () => {
    const handleChange = vi.fn()
    render(
      <TestWrapper>
        <AutoSuggestInput 
          value="" 
          onChange={handleChange} 
          suggestions={mockSuggestions as any} 
          placeholder="Search patients..." 
        />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('Search patients...')
    fireEvent.change(input, { target: { value: 'John' } })

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /John\s*Doe/i })).toBeInTheDocument()
    })
  })
})

describe('SpectacleShowcase', () => {
  const handlers = {
    onAddToCart: vi.fn(),
    onTryOn: vi.fn(),
    onCompare: vi.fn()
  }

  beforeEach(() => {
    ;(fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ items: [mockSpectacle] })
    })
  })

  it('renders spectacle items after load', async () => {
    render(
      <TestWrapper>
        <SpectacleShowcase {...handlers} />
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText('Ray-Ban Aviator Classic')).toBeInTheDocument()
    })
  })
})

describe('SpectacleCompare', () => {
  const mockProps = {
    spectacles: [mockSpectacle as any],
    isOpen: true,
    onClose: vi.fn(),
    onAddToCart: vi.fn(),
    onTryOn: vi.fn()
  }

  it('renders comparison modal', () => {
    render(
      <TestWrapper>
        <SpectacleCompare {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('Compare Spectacles')).toBeInTheDocument()
    expect(screen.getByText('Ray-Ban Aviator Classic')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(
      <TestWrapper>
        <SpectacleCompare {...mockProps} />
      </TestWrapper>
    )

    const buttons = screen.getAllByRole('button')
    fireEvent.click(buttons[0])
    expect(mockProps.onClose).toHaveBeenCalled()
  })
})

describe('TryOn3DViewer', () => {
  const mockProps = {
    spectacle: mockSpectacle as any,
    onClose: vi.fn(),
    onAddToCart: vi.fn(),
    onCapture: vi.fn()
  }

  beforeEach(() => {
    ;(navigator.mediaDevices.getUserMedia as any) = vi.fn().mockResolvedValue('mocked-stream')
  })

  it('shows initializing state', async () => {
    render(
      <TestWrapper>
        <TryOn3DViewer {...mockProps} />
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText('Initializing camera...')).toBeInTheDocument()
    })
  })
})

describe('InventoryUploader', () => {
  const mockProps = {
    onUploadComplete: vi.fn(),
    category: 'spectacles' as const
  }

  it('renders upload sections', () => {
    render(
      <TestWrapper>
        <InventoryUploader {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('Upload Spectacles')).toBeInTheDocument()
    expect(screen.getByText('Upload Files')).toBeInTheDocument()
    expect(screen.getByText('Upload CSV')).toBeInTheDocument()
  })
})

describe('ImageEntryForm', () => {
  const mockProps = {
    onClose: vi.fn(),
    onSave: vi.fn(),
    productType: 'spectacle' as const
  }

  it('renders image entry modal', () => {
    render(
      <TestWrapper>
        <ImageEntryForm {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('Add Product via Image')).toBeInTheDocument()
    expect(screen.getByText('Upload Image')).toBeInTheDocument()
    expect(screen.getByText('Take Photo')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(
      <TestWrapper>
        <ImageEntryForm {...mockProps} />
      </TestWrapper>
    )

    const buttons = screen.getAllByRole('button')
    fireEvent.click(buttons[0])
    expect(mockProps.onClose).toHaveBeenCalled()
  })
})
