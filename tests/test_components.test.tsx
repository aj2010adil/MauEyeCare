import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

// Mock components
import PrescriptionTable from '../src/components/prescriptions/PrescriptionTable'
import PrescriptionModal from '../src/components/prescriptions/PrescriptionModal'
import PrescriptionCard from '../src/components/prescriptions/PrescriptionCard'
import PrescriptionExporter from '../src/components/prescriptions/PrescriptionExporter'
import QRCodeStamp from '../src/components/ui/QRCodeStamp'
import AutoSuggestInput from '../src/components/ui/AutoSuggestInput'
import SpectacleShowcase from '../src/components/spectacles/SpectacleShowcase'
import SpectacleCompare from '../src/components/spectacles/SpectacleCompare'
import TryOn3DViewer from '../src/components/spectacles/TryOn3DViewer'
import InventoryUploader from '../src/components/inventory/InventoryUploader'
import ImageEntryForm from '../src/components/inventory/ImageEntryForm'

// Mock data
const mockPatient = {
  id: 1,
  first_name: 'John',
  last_name: 'Doe',
  phone: '1234567890',
  age: 35,
  gender: 'Male',
  created_at: '2024-01-01T00:00:00Z'
}

const mockPrescription = {
  id: 1,
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
    spectacles_total: 8500.0,
    medicines_total: 150.0,
    grand_total: 8650.0
  },
  created_at: '2024-01-01T00:00:00Z'
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
  in_stock: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Mock fetch
global.fetch = vi.fn()

// Wrapper component for testing
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    {children}
    <Toaster />
  </BrowserRouter>
)

describe('PrescriptionTable', () => {
  const mockProps = {
    prescriptions: [mockPrescription],
    patients: [mockPatient],
    onEdit: vi.fn(),
    onView: vi.fn(),
    onDownloadPDF: vi.fn()
  }

  it('renders prescription table correctly', () => {
    render(
      <TestWrapper>
        <PrescriptionTable {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Ray-Ban Aviator Classic')).toBeInTheDocument()
    expect(screen.getByText('₹8,500.00')).toBeInTheDocument()
  })

  it('calls onEdit when edit button is clicked', () => {
    render(
      <TestWrapper>
        <PrescriptionTable {...mockProps} />
      </TestWrapper>
    )

    const editButton = screen.getByLabelText('Edit prescription')
    fireEvent.click(editButton)
    expect(mockProps.onEdit).toHaveBeenCalledWith(mockPrescription.id)
  })

  it('calls onView when view button is clicked', () => {
    render(
      <TestWrapper>
        <PrescriptionTable {...mockProps} />
      </TestWrapper>
    )

    const viewButton = screen.getByLabelText('View prescription')
    fireEvent.click(viewButton)
    expect(mockProps.onView).toHaveBeenCalledWith(mockPrescription.id)
  })
})

describe('PrescriptionCard', () => {
  const mockProps = {
    prescription: mockPrescription,
    patient: mockPatient,
    onView: vi.fn(),
    onDownloadPDF: vi.fn()
  }

  it('renders prescription card correctly', () => {
    render(
      <TestWrapper>
        <PrescriptionCard {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Ray-Ban Aviator Classic')).toBeInTheDocument()
    expect(screen.getByText('₹8,650.00')).toBeInTheDocument()
  })

  it('calls onView when view button is clicked', () => {
    render(
      <TestWrapper>
        <PrescriptionCard {...mockProps} />
      </TestWrapper>
    )

    const viewButton = screen.getByText('View')
    fireEvent.click(viewButton)
    expect(mockProps.onView).toHaveBeenCalledWith(mockPrescription.id)
  })
})

describe('PrescriptionModal', () => {
  const mockProps = {
    isOpen: true,
    onClose: vi.fn(),
    onSubmit: vi.fn(),
    prescription: null
  }

  beforeEach(() => {
    // Mock fetch responses
    ;(fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        patients: [mockPatient],
        visits: [{ id: 1, patient_id: 1, issue: 'Test issue' }]
      })
    })
  })

  it('renders modal when open', () => {
    render(
      <TestWrapper>
        <PrescriptionModal {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('New Prescription')).toBeInTheDocument()
    expect(screen.getByLabelText('Patient')).toBeInTheDocument()
    expect(screen.getByLabelText('Visit')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(
      <TestWrapper>
        <PrescriptionModal {...mockProps} />
      </TestWrapper>
    )

    const closeButton = screen.getByLabelText('Close modal')
    fireEvent.click(closeButton)
    expect(mockProps.onClose).toHaveBeenCalled()
  })
})

describe('PrescriptionExporter', () => {
  const mockProps = {
    prescription: mockPrescription,
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
    expect(screen.getByText('HTML')).toBeInTheDocument()
    expect(screen.getByText('PDF')).toBeInTheDocument()
    expect(screen.getByText('DOCX')).toBeInTheDocument()
  })

  it('shows preview when HTML is selected', async () => {
    render(
      <TestWrapper>
        <PrescriptionExporter {...mockProps} />
      </TestWrapper>
    )

    const htmlButton = screen.getByText('HTML')
    fireEvent.click(htmlButton)

    await waitFor(() => {
      expect(screen.getByText('Preview')).toBeInTheDocument()
    })
  })
})

describe('QRCodeStamp', () => {
  const mockProps = {
    url: 'http://localhost:5173/prescription?id=1',
    size: 200,
    onDownload: vi.fn(),
    onCopy: vi.fn()
  }

  it('renders QR code', () => {
    render(
      <TestWrapper>
        <QRCodeStamp {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('QR Code')).toBeInTheDocument()
    expect(screen.getByText('Download')).toBeInTheDocument()
    expect(screen.getByText('Copy URL')).toBeInTheDocument()
  })

  it('calls onDownload when download button is clicked', () => {
    render(
      <TestWrapper>
        <QRCodeStamp {...mockProps} />
      </TestWrapper>
    )

    const downloadButton = screen.getByText('Download')
    fireEvent.click(downloadButton)
    expect(mockProps.onDownload).toHaveBeenCalled()
  })
})

describe('AutoSuggestInput', () => {
  const mockSuggestions = [
    { id: 1, text: 'John Doe', type: 'patient' },
    { id: 2, text: 'Jane Smith', type: 'patient' }
  ]

  const mockProps = {
    label: 'Patient Name',
    placeholder: 'Search patients...',
    suggestions: mockSuggestions,
    onSelect: vi.fn(),
    onInputChange: vi.fn()
  }

  it('renders input field', () => {
    render(
      <TestWrapper>
        <AutoSuggestInput {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByLabelText('Patient Name')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Search patients...')).toBeInTheDocument()
  })

  it('shows suggestions when typing', async () => {
    render(
      <TestWrapper>
        <AutoSuggestInput {...mockProps} />
      </TestWrapper>
    )

    const input = screen.getByPlaceholderText('Search patients...')
    fireEvent.change(input, { target: { value: 'John' } })

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })
  })
})

describe('SpectacleShowcase', () => {
  const mockProps = {
    spectacles: [mockSpectacle],
    onAddToCart: vi.fn(),
    onTryOn: vi.fn(),
    onCompare: vi.fn()
  }

  it('renders spectacle grid', () => {
    render(
      <TestWrapper>
        <SpectacleShowcase {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('Spectacle Showcase')).toBeInTheDocument()
    expect(screen.getByText('Ray-Ban Aviator Classic')).toBeInTheDocument()
    expect(screen.getByText('₹8,500.00')).toBeInTheDocument()
  })

  it('calls onAddToCart when add to cart button is clicked', () => {
    render(
      <TestWrapper>
        <SpectacleShowcase {...mockProps} />
      </TestWrapper>
    )

    const addToCartButton = screen.getByText('Add to Cart')
    fireEvent.click(addToCartButton)
    expect(mockProps.onAddToCart).toHaveBeenCalledWith(mockSpectacle)
  })
})

describe('SpectacleCompare', () => {
  const mockProps = {
    spectacles: [mockSpectacle],
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

    const closeButton = screen.getByLabelText('Close comparison')
    fireEvent.click(closeButton)
    expect(mockProps.onClose).toHaveBeenCalled()
  })
})

describe('TryOn3DViewer', () => {
  const mockProps = {
    spectacle: mockSpectacle,
    isOpen: true,
    onClose: vi.fn(),
    onAddToCart: vi.fn()
  }

  it('renders try-on modal', () => {
    render(
      <TestWrapper>
        <TryOn3DViewer {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('3D Try-On')).toBeInTheDocument()
    expect(screen.getByText('Ray-Ban Aviator Classic')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(
      <TestWrapper>
        <TryOn3DViewer {...mockProps} />
      </TestWrapper>
    )

    const closeButton = screen.getByLabelText('Close try-on')
    fireEvent.click(closeButton)
    expect(mockProps.onClose).toHaveBeenCalled()
  })
})

describe('InventoryUploader', () => {
  const mockProps = {
    isOpen: true,
    onClose: vi.fn(),
    onUploadComplete: vi.fn()
  }

  it('renders upload modal', () => {
    render(
      <TestWrapper>
        <InventoryUploader {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('Upload Inventory')).toBeInTheDocument()
    expect(screen.getByText('Upload Files')).toBeInTheDocument()
    expect(screen.getByText('Upload CSV')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(
      <TestWrapper>
        <InventoryUploader {...mockProps} />
      </TestWrapper>
    )

    const closeButton = screen.getByLabelText('Close upload')
    fireEvent.click(closeButton)
    expect(mockProps.onClose).toHaveBeenCalled()
  })
})

describe('ImageEntryForm', () => {
  const mockProps = {
    isOpen: true,
    onClose: vi.fn(),
    onSave: vi.fn()
  }

  it('renders image entry modal', () => {
    render(
      <TestWrapper>
        <ImageEntryForm {...mockProps} />
      </TestWrapper>
    )

    expect(screen.getByText('Add Product by Image')).toBeInTheDocument()
    expect(screen.getByText('Upload Image')).toBeInTheDocument()
    expect(screen.getByText('Take Photo')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(
      <TestWrapper>
        <ImageEntryForm {...mockProps} />
      </TestWrapper>
    )

    const closeButton = screen.getByLabelText('Close image entry')
    fireEvent.click(closeButton)
    expect(mockProps.onClose).toHaveBeenCalled()
  })
})
