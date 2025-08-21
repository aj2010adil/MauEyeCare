import React from 'react'
import { Download, Eye, Calendar, User, Pill, Glasses, ChevronUp, ChevronDown } from 'lucide-react'

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

interface PrescriptionTableProps {
  prescriptions: Prescription[]
  onDownload: (prescriptionId: number, patientName: string) => void
  sortBy: 'date' | 'patient' | 'type'
  sortOrder: 'asc' | 'desc'
}

export default function PrescriptionTable({ 
  prescriptions, 
  onDownload, 
  sortBy, 
  sortOrder 
}: PrescriptionTableProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
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

  const getPrescriptionTypeIcon = (type: string) => {
    switch (type) {
      case 'Complete':
        return <div className="flex items-center gap-1"><Pill size={14} /><Glasses size={14} /></div>
      case 'Medicine':
        return <Pill size={16} />
      case 'Spectacles':
        return <Glasses size={16} />
      case 'Rx Only':
        return <Eye size={16} />
      default:
        return <Calendar size={16} />
    }
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

  const getSortIcon = (field: string) => {
    if (sortBy !== field) return null
    return sortOrder === 'asc' ? <ChevronUp size={16} /> : <ChevronDown size={16} />
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <div className="flex items-center gap-1">
                <User size={14} />
                Patient
              </div>
            </th>
            <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <div className="flex items-center gap-1">
                <Calendar size={14} />
                Date
              </div>
            </th>
            <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Details
            </th>
            <th className="px-6 py-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {prescriptions.map((prescription) => {
            const prescriptionType = getPrescriptionType(prescription)
            const patientName = `${prescription.patient.first_name} ${prescription.patient.last_name || ''}`.trim()
            
            return (
              <tr key={prescription.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center">
                        <span className="text-sm font-medium text-white">
                          {patientName.split(' ').map(n => n[0]).join('').toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">{patientName}</div>
                      {prescription.patient.phone && (
                        <div className="text-sm text-gray-500">{prescription.patient.phone}</div>
                      )}
                    </div>
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(prescription.created_at)}
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getPrescriptionTypeColor(prescriptionType)}`}>
                    {getPrescriptionTypeIcon(prescriptionType)}
                    <span className="ml-1">{prescriptionType}</span>
                  </span>
                </td>
                
                <td className="px-6 py-4 text-sm text-gray-900">
                  <div className="space-y-1">
                    {prescription.rx_values && (
                      <div className="flex items-center gap-2">
                        <Eye size={14} className="text-blue-500" />
                        <span>RX Data Available</span>
                      </div>
                    )}
                    {prescription.medicines && Object.keys(prescription.medicines).length > 0 && (
                      <div className="flex items-center gap-2">
                        <Pill size={14} className="text-green-500" />
                        <span>{Object.keys(prescription.medicines).length} Medicine(s)</span>
                      </div>
                    )}
                    {prescription.spectacles && prescription.spectacles.length > 0 && (
                      <div className="flex items-center gap-2">
                        <Glasses size={14} className="text-purple-500" />
                        <span>{prescription.spectacles.length} Spectacle(s)</span>
                      </div>
                    )}
                    {prescription.totals && (
                      <div className="text-xs text-gray-500">
                        Total: ₹{prescription.totals.total || 0}
                      </div>
                    )}
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end gap-2">
                    {prescription.pdf_path && (
                      <>
                        <button
                          onClick={() => onDownload(prescription.id, patientName)}
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                        >
                          <Download size={14} className="mr-1" />
                          PDF
                        </button>
                        <button
                          onClick={() => window.open(`/api/prescriptions/${prescription.id}/pdf`, '_blank')}
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
                        >
                          <Eye size={14} className="mr-1" />
                          View
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => {/* TODO: Edit prescription */}}
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                    >
                      Edit
                    </button>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
