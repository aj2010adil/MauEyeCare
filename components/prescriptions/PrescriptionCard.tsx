import React from 'react'
import { Download, Eye, Calendar, User, Pill, Glasses, ChevronRight } from 'lucide-react'

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

interface PrescriptionCardProps {
  prescription: Prescription
  onDownload: (prescriptionId: number, patientName: string) => void
  onClick?: () => void
  onExport?: (p: Prescription) => void
  onShowQR?: (id: number, patientName: string) => void
}

export default function PrescriptionCard({ prescription, onDownload, onClick, onExport, onShowQR }: PrescriptionCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getPrescriptionType = (prescription: Prescription) => {
    const hasMedicines = prescription.medicines && Object.keys(prescription.medicines).length > 0
    const hasSpectacles = prescription.spectacles && prescription.spectacles.length > 0
    const hasRx = prescription.rx_values && Object.keys(prescription.rx_values).length > 0
    
    if (hasMedicines && hasSpectacles) return 'Complete'
    if (hasMedicines) return 'Medicine'
    if (hasSpectacles) return 'Spectacles'
    if (hasRx) return 'Rx Only'
    return 'Basic'
  }

  const getPrescriptionTypeColor = (type: string) => {
    switch (type) {
      case 'Complete':
        return 'bg-green-100 text-green-700 border-green-200'
      case 'Medicine':
        return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'Spectacles':
        return 'bg-purple-100 text-purple-700 border-purple-200'
      case 'Rx Only':
        return 'bg-orange-100 text-orange-700 border-orange-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const prescriptionType = getPrescriptionType(prescription)
  const patientName = `${prescription.patient.first_name} ${prescription.patient.last_name || ''}`.trim()

  return (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center">
            <span className="text-sm font-medium text-white">
              {patientName.split(' ').map(n => n[0]).join('').toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{patientName}</h3>
            {prescription.patient.phone && (
              <p className="text-sm text-gray-500">{prescription.patient.phone}</p>
            )}
          </div>
        </div>
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getPrescriptionTypeColor(prescriptionType)}`}>
          {prescriptionType}
        </span>
      </div>

      {/* Date */}
      <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
        <Calendar size={14} />
        <span>{formatDate(prescription.created_at)}</span>
      </div>

      {/* Details */}
      <div className="space-y-2 mb-4">
        {prescription.rx_values && (
          <div className="flex items-center gap-2 text-sm">
            <Eye size={14} className="text-blue-500" />
            <span className="text-gray-700">RX Data Available</span>
          </div>
        )}
        {prescription.medicines && Object.keys(prescription.medicines).length > 0 && (
          <div className="flex items-center gap-2 text-sm">
            <Pill size={14} className="text-green-500" />
            <span className="text-gray-700">{Object.keys(prescription.medicines).length} Medicine(s)</span>
          </div>
        )}
        {prescription.spectacles && prescription.spectacles.length > 0 && (
          <div className="flex items-center gap-2 text-sm">
            <Glasses size={14} className="text-purple-500" />
            <span className="text-gray-700">{prescription.spectacles.length} Spectacle(s)</span>
          </div>
        )}
        {prescription.totals && (
          <div className="text-sm font-medium text-gray-900">
            Total: ₹{prescription.totals.total || 0}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <div className="flex items-center gap-2">
          {prescription.pdf_path && (
            <>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDownload(prescription.id, patientName)
                }}
                className="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 transition-colors"
              >
                <Download size={12} className="mr-1" />
                PDF
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  window.open(`/api/prescriptions/${prescription.id}/pdf`, '_blank')
                }}
                className="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
              >
                <Eye size={12} className="mr-1" />
                View
              </button>
            </>
          )}
          {onExport && (
            <button
              onClick={(e) => { e.stopPropagation(); onExport(prescription) }}
              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-colors"
            >
              Export
            </button>
          )}
          {onShowQR && (
            <button
              onClick={(e) => { e.stopPropagation(); onShowQR(prescription.id, patientName) }}
              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-colors"
            >
              QR
            </button>
          )}
        </div>
        <ChevronRight size={16} className="text-gray-400" />
      </div>
    </div>
  )
}
