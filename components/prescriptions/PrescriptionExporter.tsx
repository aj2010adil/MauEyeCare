import React, { useState } from 'react'
import { Download, FileText, FileImage, FileCode, QrCode, Eye, X } from 'lucide-react'
import { useAuth } from '../../AuthContext'
import toast from 'react-hot-toast'

interface Patient {
  id: number
  first_name: string
  last_name: string
  phone?: string
  email?: string
  date_of_birth?: string
  gender?: string
  address?: string
}

interface Prescription {
  id: number
  patient: Patient
  visit_date: string
  rx_values: {
    od_sphere?: number
    od_cylinder?: number
    od_axis?: number
    od_add?: number
    os_sphere?: number
    os_cylinder?: number
    os_axis?: number
    os_add?: number
  }
  spectacles: Array<{
    name: string
    price: number
    quantity: number
  }>
  medicines: Record<string, {
    name: string
    dosage: string
    quantity: number
    price: number
  }>
  totals: {
    spectacles_total: number
    medicines_total: number
    grand_total: number
  }
  doctor_signature?: string
  notes?: string
  created_at: string
}

interface PrescriptionExporterProps {
  prescription: Prescription
  onClose: () => void
}

export default function PrescriptionExporter({ prescription, onClose }: PrescriptionExporterProps) {
  const { accessToken } = useAuth()
  const [exportFormat, setExportFormat] = useState<'html' | 'pdf' | 'docx'>('html')
  const [isExporting, setIsExporting] = useState(false)
  const [previewHtml, setPreviewHtml] = useState<string>('')

  const generateHTML = () => {
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prescription - ${prescription.patient.first_name} ${prescription.patient.last_name}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .prescription-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .clinic-name {
            font-size: 28px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 5px;
        }
        .clinic-address {
            font-size: 14px;
            color: #6b7280;
            line-height: 1.4;
        }
        .clinic-contact {
            font-size: 14px;
            color: #6b7280;
            margin-top: 5px;
        }
        .patient-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background-color: #f8fafc;
            border-radius: 8px;
        }
        .info-group {
            display: flex;
            flex-direction: column;
        }
        .info-label {
            font-weight: bold;
            color: #374151;
            margin-bottom: 5px;
        }
        .info-value {
            color: #1f2937;
        }
        .rx-section {
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 15px;
            border-bottom: 2px solid #dbeafe;
            padding-bottom: 5px;
        }
        .rx-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .rx-table th,
        .rx-table td {
            border: 1px solid #d1d5db;
            padding: 12px;
            text-align: center;
        }
        .rx-table th {
            background-color: #f3f4f6;
            font-weight: bold;
            color: #374151;
        }
        .rx-table td {
            background-color: white;
        }
        .items-section {
            margin-bottom: 30px;
        }
        .items-table {
            width: 100%;
            border-collapse: collapse;
        }
        .items-table th,
        .items-table td {
            border: 1px solid #d1d5db;
            padding: 10px;
            text-align: left;
        }
        .items-table th {
            background-color: #f3f4f6;
            font-weight: bold;
            color: #374151;
        }
        .total-section {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 30px;
        }
        .total-table {
            border-collapse: collapse;
        }
        .total-table td {
            padding: 8px 15px;
            border: none;
        }
        .total-table .total-row {
            font-weight: bold;
            border-top: 2px solid #d1d5db;
        }
        .footer {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
        }
        .signature-section {
            text-align: center;
        }
        .signature-line {
            width: 200px;
            border-bottom: 1px solid #000;
            margin-bottom: 5px;
        }
        .qr-section {
            text-align: center;
        }
        .qr-code {
            width: 80px;
            height: 80px;
            background-color: #f3f4f6;
            border: 1px solid #d1d5db;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 5px;
        }
        .notes-section {
            margin-top: 20px;
            padding: 15px;
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 4px;
        }
        @media print {
            body {
                background-color: white;
                padding: 0;
            }
            .prescription-container {
                box-shadow: none;
                border-radius: 0;
            }
        }
    </style>
</head>
<body>
    <div class="prescription-container">
        <div class="header">
            <div class="clinic-name">MAU Eye Care</div>
            <div class="clinic-address">
                Mubarakpur Azamgarh<br>
                Pura Sofi Bhonu Kuraishi Dasai Kuwa<br>
                Azamgarh, Uttar Pradesh
            </div>
            <div class="clinic-contact">
                📞 092356 47410 | 🌐 www.facebook.com
            </div>
        </div>

        <div class="patient-info">
            <div class="info-group">
                <span class="info-label">Patient Name:</span>
                <span class="info-value">${prescription.patient.first_name} ${prescription.patient.last_name}</span>
            </div>
            <div class="info-group">
                <span class="info-label">Visit Date:</span>
                <span class="info-value">${new Date(prescription.visit_date).toLocaleDateString()}</span>
            </div>
            <div class="info-group">
                <span class="info-label">Phone:</span>
                <span class="info-value">${prescription.patient.phone || 'N/A'}</span>
            </div>
            <div class="info-group">
                <span class="info-label">Prescription ID:</span>
                <span class="info-value">#${prescription.id}</span>
            </div>
        </div>

        <div class="rx-section">
            <div class="section-title">Prescription Details</div>
            <table class="rx-table">
                <thead>
                    <tr>
                        <th>Eye</th>
                        <th>Sphere</th>
                        <th>Cylinder</th>
                        <th>Axis</th>
                        <th>Add</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>OD (Right)</strong></td>
                        <td>${prescription.rx_values.od_sphere || '0.00'}</td>
                        <td>${prescription.rx_values.od_cylinder || '0.00'}</td>
                        <td>${prescription.rx_values.od_axis || '0'}</td>
                        <td>${prescription.rx_values.od_add || '0.00'}</td>
                    </tr>
                    <tr>
                        <td><strong>OS (Left)</strong></td>
                        <td>${prescription.rx_values.os_sphere || '0.00'}</td>
                        <td>${prescription.rx_values.os_cylinder || '0.00'}</td>
                        <td>${prescription.rx_values.os_axis || '0'}</td>
                        <td>${prescription.rx_values.os_add || '0.00'}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        ${prescription.spectacles.length > 0 ? `
        <div class="items-section">
            <div class="section-title">Spectacles</div>
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${prescription.spectacles.map(spectacle => `
                        <tr>
                            <td>${spectacle.name}</td>
                            <td>${spectacle.quantity}</td>
                            <td>₹${spectacle.price.toLocaleString()}</td>
                            <td>₹${(spectacle.price * spectacle.quantity).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        ` : ''}

        ${Object.keys(prescription.medicines).length > 0 ? `
        <div class="items-section">
            <div class="section-title">Medicines</div>
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Medicine</th>
                        <th>Dosage</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(prescription.medicines).map(([key, medicine]) => `
                        <tr>
                            <td>${medicine.name}</td>
                            <td>${medicine.dosage}</td>
                            <td>${medicine.quantity}</td>
                            <td>₹${medicine.price.toLocaleString()}</td>
                            <td>₹${(medicine.price * medicine.quantity).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        ` : ''}

        <div class="total-section">
            <table class="total-table">
                ${prescription.spectacles.length > 0 ? `
                <tr>
                    <td>Spectacles Total:</td>
                    <td>₹${prescription.totals.spectacles_total.toLocaleString()}</td>
                </tr>
                ` : ''}
                ${Object.keys(prescription.medicines).length > 0 ? `
                <tr>
                    <td>Medicines Total:</td>
                    <td>₹${prescription.totals.medicines_total.toLocaleString()}</td>
                </tr>
                ` : ''}
                <tr class="total-row">
                    <td>Grand Total:</td>
                    <td>₹${prescription.totals.grand_total.toLocaleString()}</td>
                </tr>
            </table>
        </div>

        ${prescription.notes ? `
        <div class="notes-section">
            <strong>Notes:</strong> ${prescription.notes}
        </div>
        ` : ''}

        <div class="footer">
            <div class="signature-section">
                <div class="signature-line"></div>
                <div>Doctor's Signature</div>
            </div>
            <div class="qr-section">
                <div class="qr-code">
                    <QrCode size={40} />
                </div>
                <div style="font-size: 10px; color: #6b7280;">
                    Scan to view online
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    `
    return html
  }

  const exportPrescription = async () => {
    setIsExporting(true)
    
    try {
      const response = await fetch(`/api/prescriptions/${prescription.id}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          format: exportFormat,
          include_qr: true,
          branding: {
            clinic_name: 'MAU Eye Care',
            address: 'Mubarakpur Azamgarh, Pura Sofi Bhonu Kuraishi Dasai Kuwa, Azamgarh, Uttar Pradesh',
            phone: '092356 47410',
            website: 'www.facebook.com'
          }
        }),
      })

      if (!response.ok) throw new Error('Export failed')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `prescription-${prescription.patient.first_name}-${prescription.patient.last_name}-${prescription.id}.${exportFormat}`
      link.click()
      window.URL.revokeObjectURL(url)

      toast.success(`Prescription exported as ${exportFormat.toUpperCase()}`)
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Failed to export prescription')
    } finally {
      setIsExporting(false)
    }
  }

  const previewHTML = () => {
    const html = generateHTML()
    setPreviewHtml(html)
  }

  const closePreview = () => {
    setPreviewHtml('')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Export Prescription</h2>
            <p className="text-gray-600">
              {prescription.patient.first_name} {prescription.patient.last_name} - {new Date(prescription.visit_date).toLocaleDateString()}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Format Selection */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Format</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => setExportFormat('html')}
                className={`p-4 border-2 rounded-lg transition-colors ${
                  exportFormat === 'html'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileCode className="mx-auto mb-2" size={32} />
                <div className="text-center">
                  <div className="font-semibold">HTML</div>
                  <div className="text-sm text-gray-600">Web format</div>
                </div>
              </button>

              <button
                onClick={() => setExportFormat('pdf')}
                className={`p-4 border-2 rounded-lg transition-colors ${
                  exportFormat === 'pdf'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileText className="mx-auto mb-2" size={32} />
                <div className="text-center">
                  <div className="font-semibold">PDF</div>
                  <div className="text-sm text-gray-600">Print format</div>
                </div>
              </button>

              <button
                onClick={() => setExportFormat('docx')}
                className={`p-4 border-2 rounded-lg transition-colors ${
                  exportFormat === 'docx'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileImage className="mx-auto mb-2" size={32} />
                <div className="text-center">
                  <div className="font-semibold">DOCX</div>
                  <div className="text-sm text-gray-600">Word format</div>
                </div>
              </button>
            </div>
          </div>

          {/* Preview Button for HTML */}
          {exportFormat === 'html' && (
            <div className="flex justify-center">
              <button
                onClick={previewHTML}
                className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
              >
                <Eye size={20} />
                Preview HTML
              </button>
            </div>
          )}

          {/* Export Button */}
          <div className="flex justify-center">
            <button
              onClick={exportPrescription}
              disabled={isExporting}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <Download size={20} />
              {isExporting ? 'Exporting...' : `Export as ${exportFormat.toUpperCase()}`}
            </button>
          </div>

          {/* Features */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-3">Export Features</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <QrCode size={16} className="text-blue-600" />
                QR code linking to online prescription
              </li>
              <li className="flex items-center gap-2">
                <FileText size={16} className="text-green-600" />
                Professional branding with clinic details
              </li>
              <li className="flex items-center gap-2">
                <FileImage size={16} className="text-purple-600" />
                Complete prescription details and totals
              </li>
              <li className="flex items-center gap-2">
                <Download size={16} className="text-orange-600" />
                Ready for printing or digital sharing
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* HTML Preview Modal */}
      {previewHtml && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">HTML Preview</h3>
              <button
                onClick={closePreview}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            <div className="h-[calc(90vh-80px)] overflow-auto">
              <iframe
                srcDoc={previewHtml}
                className="w-full h-full border-0"
                title="Prescription Preview"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
