import React, { useState, useEffect } from 'react'
import { Download, Copy, QrCode, Settings, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../AuthContext'

interface QRCodeStampProps {
  prescriptionId: number
  patientName: string
  onClose: () => void
  size?: number
  includeLogo?: boolean
  logoUrl?: string
}

export default function QRCodeStamp({ 
  prescriptionId, 
  patientName, 
  onClose, 
  size = 200,
  includeLogo = true,
  logoUrl
}: QRCodeStampProps) {
  const { accessToken } = useAuth()
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(true)
  const [qrSettings, setQrSettings] = useState({
    foregroundColor: '#000000',
    backgroundColor: '#FFFFFF',
    errorCorrectionLevel: 'M' as 'L' | 'M' | 'Q' | 'H',
    margin: 2,
    scale: 8
  })

  useEffect(() => {
    generateQRCode()
  }, [prescriptionId, qrSettings])

  const generateQRCode = async () => {
    setIsGenerating(true)
    try {
      const params = new URLSearchParams({
        size: String(size),
        foreground_color: qrSettings.foregroundColor,
        background_color: qrSettings.backgroundColor,
      })
      const resp = await fetch(
        `/api/inventory/prescriptions/${prescriptionId}/qr.png?${params.toString()}`,
        {
          headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
        }
      )
      if (!resp.ok) throw new Error('QR API failed')
      const blob = await resp.blob()
      const dataUrl = URL.createObjectURL(blob)
      setQrCodeDataUrl(dataUrl)
    } catch (error) {
      console.error('Error generating QR code:', error)
      toast.error('Failed to generate QR code')
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadQRCode = () => {
    if (!qrCodeDataUrl) return

    const link = document.createElement('a')
    link.download = `qr-prescription-${prescriptionId}.png`
    link.href = qrCodeDataUrl
    link.click()
  }

  const copyQRCodeUrl = async () => {
    const prescriptionUrl = `${window.location.origin}/prescription?id=${prescriptionId}`
    
    try {
      await navigator.clipboard.writeText(prescriptionUrl)
      toast.success('Prescription URL copied to clipboard')
    } catch (error) {
      console.error('Error copying URL:', error)
      toast.error('Failed to copy URL')
    }
  }

  const copyQRCodeImage = async () => {
    if (!qrCodeDataUrl) return

    try {
      const response = await fetch(qrCodeDataUrl)
      const blob = await response.blob()
      await navigator.clipboard.write([
        new ClipboardItem({
          'image/png': blob
        })
      ])
      toast.success('QR code image copied to clipboard')
    } catch (error) {
      console.error('Error copying QR code image:', error)
      toast.error('Failed to copy QR code image')
    }
  }

  const generateCustomQRCode = () => {
    // This would integrate with a proper QR code library like qrcode.js
    // For now, we'll regenerate with current settings
    generateQRCode()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <QrCode className="text-blue-600" size={24} />
            <div>
              <h2 className="text-xl font-bold text-gray-900">QR Code</h2>
              <p className="text-sm text-gray-600">Prescription #{prescriptionId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* QR Code Display */}
          <div className="flex justify-center">
            <div className="relative">
              {isGenerating ? (
                <div className="w-48 h-48 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : (
                <div className="relative">
                  <img
                    src={qrCodeDataUrl}
                    alt={`QR Code for prescription ${prescriptionId}`}
                    className="w-48 h-48 border border-gray-200 rounded-lg"
                  />
                  {includeLogo && logoUrl && (
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                      <img
                        src={logoUrl}
                        alt="Clinic Logo"
                        className="w-8 h-8 bg-white rounded-full p-1 border border-gray-200"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* QR Code Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">QR Code Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Patient:</span>
                <span className="font-medium">{patientName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Prescription ID:</span>
                <span className="font-medium">#{prescriptionId}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">URL:</span>
                <span className="font-mono text-xs text-blue-600 truncate max-w-32">
                  /prescription?id={prescriptionId}
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={downloadQRCode}
              disabled={!qrCodeDataUrl}
              className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Download size={20} />
              Download QR Code
            </button>
            
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={copyQRCodeUrl}
                className="py-2 px-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center gap-2"
              >
                <Copy size={16} />
                Copy URL
              </button>
              <button
                onClick={copyQRCodeImage}
                disabled={!qrCodeDataUrl}
                className="py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Copy size={16} />
                Copy Image
              </button>
            </div>
          </div>

          {/* QR Code Settings */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Customize</h3>
              <Settings size={16} className="text-gray-400" />
            </div>
            
            <div className="space-y-3">
              {/* Color Settings */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Foreground Color
                  </label>
                  <input
                    type="color"
                    value={qrSettings.foregroundColor}
                    onChange={(e) => setQrSettings(prev => ({ ...prev, foregroundColor: e.target.value }))}
                    className="w-full h-8 border border-gray-300 rounded cursor-pointer"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Background Color
                  </label>
                  <input
                    type="color"
                    value={qrSettings.backgroundColor}
                    onChange={(e) => setQrSettings(prev => ({ ...prev, backgroundColor: e.target.value }))}
                    className="w-full h-8 border border-gray-300 rounded cursor-pointer"
                  />
                </div>
              </div>

              {/* Error Correction Level */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Error Correction
                </label>
                <select
                  value={qrSettings.errorCorrectionLevel}
                  onChange={(e) => setQrSettings(prev => ({ ...prev, errorCorrectionLevel: e.target.value as 'L' | 'M' | 'Q' | 'H' }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="L">Low (7%)</option>
                  <option value="M">Medium (15%)</option>
                  <option value="Q">Quartile (25%)</option>
                  <option value="H">High (30%)</option>
                </select>
              </div>

              {/* Margin */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Margin: {qrSettings.margin} modules
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={qrSettings.margin}
                  onChange={(e) => setQrSettings(prev => ({ ...prev, margin: parseInt(e.target.value) }))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>

            <button
              onClick={generateCustomQRCode}
              className="w-full mt-3 py-2 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
            >
              Regenerate QR Code
            </button>
          </div>

          {/* Usage Instructions */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">How to Use</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Print and attach to prescription</li>
              <li>• Patients can scan to view online</li>
              <li>• Share digitally for easy access</li>
              <li>• Embed in documents or emails</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
