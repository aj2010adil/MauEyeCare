import { useEffect, useState } from 'react'
import { useAuth } from './AuthContext'
import { Plus, Search, Download, Eye, Calendar, User, Grid, List } from 'lucide-react'
import PrescriptionTable from './components/prescriptions/PrescriptionTable'
import PrescriptionCard from './components/prescriptions/PrescriptionCard'
import Pagination from './components/ui/Pagination'
import { useDebounce } from './useDebounce'
import PrescriptionModal from './components/prescriptions/PrescriptionModal'
import PrescriptionExporter from './components/prescriptions/PrescriptionExporter'
import QRCodeStamp from './components/prescriptions/QRCodeStamp'
import { Toaster } from 'react-hot-toast'

interface Patient {
  id: number
  first_name: string
  last_name?: string
  phone?: string
}

interface Prescription {
  id: number
  created_at: string
  pdf_path?: string
  rx_values?: any
  spectacles?: any[]
  medicines?: any
  totals?: any
  patient: Patient
}

export default function PrescriptionsPage() {
  const { accessToken } = useAuth()
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [sortBy, setSortBy] = useState<'date' | 'patient' | 'type'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table')
  const [exportingPrescription, setExportingPrescription] = useState<Prescription | null>(null)
  const [qrInfo, setQrInfo] = useState<{ id: number; patientName: string } | null>(null)
  const debouncedSearchQuery = useDebounce(searchQuery, 500)

  const load = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ 
        page: page.toString(), 
        q: debouncedSearchQuery,
        sort_by: sortBy,
        sort_order: sortOrder
      })
      const res = await fetch(`/api/prescriptions?${params.toString()}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      if (!res.ok) throw new Error('Failed to fetch prescriptions.')
      const data = await res.json()
      setPrescriptions(data.items)
      setTotalPages(Math.ceil(data.total / data.page_size))
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    load()
    if (page !== 1) {
      setPage(1)
    }
  }, [debouncedSearchQuery, sortBy, sortOrder])

  useEffect(() => { load() }, [page])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    load()
  }

  const handleSort = (field: 'date' | 'patient' | 'type') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  const downloadPDF = async (prescriptionId: number, patientName: string) => {
    try {
      const res = await fetch(`/api/prescriptions/${prescriptionId}/pdf`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      if (!res.ok) throw new Error('Failed to download PDF')
      
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Prescription_${patientName}_${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err: any) {
      console.error('Download failed:', err)
    }
  }

  return (
    <>
      <Toaster position="top-center" reverseOrder={false} />
      <PrescriptionModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onSuccess={() => {
          setIsModalOpen(false)
          load()
        }} 
      />

      {exportingPrescription && (
        <PrescriptionExporter
          prescription={exportingPrescription as any}
          onClose={() => setExportingPrescription(null)}
        />
      )}
      {qrInfo && (
        <QRCodeStamp
          prescriptionId={qrInfo.id}
          patientName={qrInfo.patientName}
          onClose={() => setQrInfo(null)}
        />
      )}
      
      <div className="min-h-screen bg-gray-50">
        {/* Header Section */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="py-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">📋 Prescriptions</h1>
                  <p className="mt-1 text-sm text-gray-500">
                    Manage and track all patient prescriptions
                  </p>
                </div>
                <button 
                  onClick={() => setIsModalOpen(true)} 
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl px-6 py-3 flex items-center gap-2 hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <Plus size={20} /> New Prescription
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Search and Filters */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="flex flex-col lg:flex-row gap-4">
                <div className="relative flex-grow">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by patient name, phone, or prescription details..."
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  />
                </div>
                <button 
                  type="submit" 
                  className="bg-gray-800 text-white font-semibold rounded-lg px-6 py-3 hover:bg-gray-900 transition-colors flex items-center gap-2"
                >
                  <Search size={18} /> Search
                </button>
              </div>
              
              {/* Sort and View Options */}
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex flex-wrap gap-2">
                  <span className="text-sm text-gray-600 font-medium">Sort by:</span>
                  <button
                    type="button"
                    onClick={() => handleSort('date')}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      sortBy === 'date' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    <Calendar size={14} className="inline mr-1" />
                    Date
                  </button>
                  <button
                    type="button"
                    onClick={() => handleSort('patient')}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      sortBy === 'patient' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    <User size={14} className="inline mr-1" />
                    Patient
                  </button>
                  <button
                    type="button"
                    onClick={() => handleSort('type')}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      sortBy === 'type' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    Type
                  </button>
                </div>
                
                {/* View Mode Toggle */}
                <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
                  <button
                    type="button"
                    onClick={() => setViewMode('table')}
                    className={`p-2 rounded-md transition-colors ${
                      viewMode === 'table' 
                        ? 'bg-white text-blue-600 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <List size={16} />
                  </button>
                  <button
                    type="button"
                    onClick={() => setViewMode('cards')}
                    className={`p-2 rounded-md transition-colors ${
                      viewMode === 'cards' 
                        ? 'bg-white text-blue-600 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Grid size={16} />
                  </button>
                </div>
              </div>
            </form>
          </div>

          {/* Content Area */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {isLoading && (
              <div className="flex items-center justify-center p-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Loading prescriptions...</span>
              </div>
            )}
            
            {error && (
              <div className="p-8 text-center">
                <div className="inline-flex items-center px-4 py-2 bg-red-100 text-red-700 rounded-lg">
                  <span className="text-sm font-medium">{error}</span>
                </div>
              </div>
            )}
            
            {!isLoading && !error && prescriptions.length === 0 && (
              <div className="p-12 text-center">
                <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <Search className="text-gray-400" size={32} />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No prescriptions found</h3>
                <p className="text-gray-500 mb-6">
                  {searchQuery ? 'Try adjusting your search terms.' : 'Get started by creating your first prescription.'}
                </p>
                {!searchQuery && (
                  <button 
                    onClick={() => setIsModalOpen(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Create Prescription
                  </button>
                )}
              </div>
            )}
            
            {!isLoading && !error && prescriptions.length > 0 && (
              <>
                {viewMode === 'table' ? (
                  <PrescriptionTable 
                    prescriptions={prescriptions} 
                    onDownload={downloadPDF}
                    sortBy={sortBy}
                    sortOrder={sortOrder}
                    onExport={(p) => setExportingPrescription(p)}
                    onShowQR={(id, name) => setQrInfo({ id, patientName: name })}
                  />
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
                    {prescriptions.map(prescription => (
                      <PrescriptionCard
                        key={prescription.id}
                        prescription={prescription}
                        onDownload={downloadPDF}
                        onExport={(p) => setExportingPrescription(p as any)}
                        onShowQR={(id, name) => setQrInfo({ id, patientName: name })}
                      />
                    ))}
                  </div>
                )}
                <div className="border-t border-gray-200 px-6 py-4">
                  <Pagination 
                    currentPage={page} 
                    totalPages={totalPages} 
                    onPageChange={setPage} 
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
