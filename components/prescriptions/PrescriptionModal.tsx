import React, { useState, useEffect } from 'react'
import { X, User, Calendar, Eye, Pill, Glasses, Plus, Trash2, Save, Loader2 } from 'lucide-react'
import { useAuth } from '../../AuthContext'
import toast from 'react-hot-toast'

interface Patient {
  id: number
  first_name: string
  last_name?: string
  phone?: string
}

interface Visit {
  id: number
  visit_date: string
  issue?: string
  advice?: string
}

interface Spectacle {
  name: string
  price: number
  quantity: number
}

interface Medicine {
  name: string
  dosage: string
  quantity: number
  price: number
}

interface FormData {
  patient_id: string
  visit_id: string
  rx_values: {
    OD: { Sphere: string; Cylinder: string; Axis: string; Add: string }
    OS: { Sphere: string; Cylinder: string; Axis: string; Add: string }
  }
  spectacles: Spectacle[]
  medicines: Record<string, Medicine>
  totals: { total: number }
}

interface PrescriptionModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function PrescriptionModal({ isOpen, onClose, onSuccess }: PrescriptionModalProps) {
  const { accessToken } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [patients, setPatients] = useState<Patient[]>([])
  const [visits, setVisits] = useState<Visit[]>([])
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)
  const [selectedVisit, setSelectedVisit] = useState<Visit | null>(null)
  
  // Form data
  const [formData, setFormData] = useState<FormData>({
    patient_id: '',
    visit_id: '',
    rx_values: {
      OD: { Sphere: '', Cylinder: '', Axis: '', Add: '' },
      OS: { Sphere: '', Cylinder: '', Axis: '', Add: '' }
    },
    spectacles: [],
    medicines: {},
    totals: { total: 0 }
  })

  // Load patients and visits
  useEffect(() => {
    if (isOpen) {
      loadPatients()
    }
  }, [isOpen])

  const loadPatients = async () => {
    try {
      const res = await fetch('/api/patients', {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      if (res.ok) {
        const data = await res.json()
        setPatients(data.items || data)
      }
    } catch (error) {
      console.error('Failed to load patients:', error)
    }
  }

  const loadVisits = async (patientId: number) => {
    try {
      const res = await fetch(`/api/patients/${patientId}/visits`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      if (res.ok) {
        const data = await res.json()
        setVisits(data)
      }
    } catch (error) {
      console.error('Failed to load visits:', error)
    }
  }

  const handlePatientChange = (patientId: string) => {
    const patient = patients.find(p => p.id.toString() === patientId)
    setSelectedPatient(patient || null)
    setSelectedVisit(null)
    setFormData(prev => ({ ...prev, patient_id: patientId, visit_id: '' }))
    
    if (patientId) {
      loadVisits(parseInt(patientId))
    } else {
      setVisits([])
    }
  }

  const handleVisitChange = (visitId: string) => {
    const visit = visits.find(v => v.id.toString() === visitId)
    setSelectedVisit(visit || null)
    setFormData(prev => ({ ...prev, visit_id: visitId }))
  }

  const updateRxValue = (eye: 'OD' | 'OS', field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      rx_values: {
        ...prev.rx_values,
        [eye]: {
          ...prev.rx_values[eye],
          [field]: value
        }
      }
    }))
  }

  const addSpectacle = () => {
    setFormData(prev => ({
      ...prev,
      spectacles: [...prev.spectacles, { name: '', price: 0, quantity: 1 }]
    }))
  }

  const updateSpectacle = (index: number, field: keyof Spectacle, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      spectacles: prev.spectacles.map((spec, i) => 
        i === index ? { ...spec, [field]: value } : spec
      )
    }))
  }

  const removeSpectacle = (index: number) => {
    setFormData(prev => ({
      ...prev,
      spectacles: prev.spectacles.filter((_, i) => i !== index)
    }))
  }

  const addMedicine = () => {
    setFormData(prev => ({
      ...prev,
      medicines: { ...prev.medicines, [`medicine_${Date.now()}`]: { name: '', dosage: '', quantity: 1, price: 0 } }
    }))
  }

  const updateMedicine = (key: string, field: keyof Medicine, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      medicines: {
        ...prev.medicines,
        [key]: { ...prev.medicines[key], [field]: value }
      }
    }))
  }

  const removeMedicine = (key: string) => {
    const { [key]: removed, ...rest } = formData.medicines
    setFormData(prev => ({ ...prev, medicines: rest }))
  }

  const calculateTotal = () => {
    const spectacleTotal = formData.spectacles.reduce((sum, spec) => sum + (spec.price * spec.quantity), 0)
    const medicineTotal = Object.values(formData.medicines).reduce((sum: number, med: Medicine) => sum + (med.price * med.quantity), 0)
    return spectacleTotal + medicineTotal
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.patient_id) {
      toast.error('Please select a patient')
      return
    }

    setIsLoading(true)
    try {
      const prescriptionData = {
        ...formData,
        patient_id: parseInt(formData.patient_id),
        visit_id: formData.visit_id ? parseInt(formData.visit_id) : null,
        totals: { total: calculateTotal() }
      }

      const res = await fetch('/api/prescriptions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(prescriptionData),
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to create prescription')
      }

      toast.success('Prescription created successfully!')
      onSuccess()
    } catch (error: any) {
      toast.error(error.message || 'Failed to create prescription')
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Create New Prescription</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Patient and Visit Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User size={16} className="inline mr-2" />
                Patient
              </label>
              <select
                value={formData.patient_id}
                onChange={(e) => handlePatientChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Select a patient</option>
                {patients.map(patient => (
                  <option key={patient.id} value={patient.id}>
                    {patient.first_name} {patient.last_name || ''} {patient.phone ? `(${patient.phone})` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar size={16} className="inline mr-2" />
                Visit (Optional)
              </label>
              <select
                value={formData.visit_id}
                onChange={(e) => handleVisitChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select a visit</option>
                {visits.map(visit => (
                  <option key={visit.id} value={visit.id}>
                    {new Date(visit.visit_date).toLocaleDateString()} - {visit.issue || 'No issue specified'}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* RX Values */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Eye size={20} className="mr-2" />
              Prescription Values
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {(['OD', 'OS'] as const).map(eye => (
                <div key={eye} className="space-y-3">
                  <h4 className="font-medium text-gray-700">{eye} (Right Eye)</h4>
                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label className="block text-xs text-gray-600">Sphere</label>
                      <input
                        type="number"
                        step="0.25"
                        value={formData.rx_values[eye].Sphere}
                        onChange={(e) => updateRxValue(eye, 'Sphere', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                        placeholder="0.00"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600">Cylinder</label>
                      <input
                        type="number"
                        step="0.25"
                        value={formData.rx_values[eye].Cylinder}
                        onChange={(e) => updateRxValue(eye, 'Cylinder', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                        placeholder="0.00"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600">Axis</label>
                      <input
                        type="number"
                        min="0"
                        max="180"
                        value={formData.rx_values[eye].Axis}
                        onChange={(e) => updateRxValue(eye, 'Axis', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Spectacles */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <Glasses size={20} className="mr-2" />
                Spectacles
              </h3>
              <button
                type="button"
                onClick={addSpectacle}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
              >
                <Plus size={16} className="mr-1" />
                Add Spectacle
              </button>
            </div>
            
            {formData.spectacles.map((spectacle, index) => (
              <div key={index} className="flex items-center gap-3 mb-3 p-3 bg-white rounded border">
                <input
                  type="text"
                  value={spectacle.name}
                  onChange={(e) => updateSpectacle(index, 'name', e.target.value)}
                  placeholder="Spectacle name"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  value={spectacle.price}
                  onChange={(e) => updateSpectacle(index, 'price', parseFloat(e.target.value) || 0)}
                  placeholder="Price"
                  className="w-24 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  value={spectacle.quantity}
                  onChange={(e) => updateSpectacle(index, 'quantity', parseInt(e.target.value) || 1)}
                  placeholder="Qty"
                  className="w-20 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={() => removeSpectacle(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>

          {/* Medicines */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <Pill size={20} className="mr-2" />
                Medicines
              </h3>
              <button
                type="button"
                onClick={addMedicine}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200"
              >
                <Plus size={16} className="mr-1" />
                Add Medicine
              </button>
            </div>
            
            {Object.entries(formData.medicines).map(([key, medicine]) => (
              <div key={key} className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3 p-3 bg-white rounded border">
                <input
                  type="text"
                  value={medicine.name}
                  onChange={(e) => updateMedicine(key, 'name', e.target.value)}
                  placeholder="Medicine name"
                  className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  value={medicine.dosage}
                  onChange={(e) => updateMedicine(key, 'dosage', e.target.value)}
                  placeholder="Dosage instructions"
                  className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  value={medicine.quantity}
                  onChange={(e) => updateMedicine(key, 'quantity', parseInt(e.target.value) || 1)}
                  placeholder="Quantity"
                  className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    value={medicine.price}
                    onChange={(e) => updateMedicine(key, 'price', parseFloat(e.target.value) || 0)}
                    placeholder="Price"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => removeMedicine(key)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Total */}
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-lg font-medium text-gray-900">Total Amount:</span>
              <span className="text-2xl font-bold text-blue-600">₹{calculateTotal().toFixed(2)}</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Save size={16} />
                  Create Prescription
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
