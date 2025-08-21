import React, { useState, useRef } from 'react'
import { Upload, FileText, X, CheckCircle, AlertCircle, Download, Plus } from 'lucide-react'
import { useAuth } from '../../AuthContext'
import toast from 'react-hot-toast'

interface InventoryItem {
  id?: number
  name: string
  brand?: string
  category: 'spectacles' | 'medicines'
  price: number
  quantity: number
  image_url?: string
  description?: string
  specifications?: Record<string, any>
}

interface InventoryUploaderProps {
  onUploadComplete: () => void
  category: 'spectacles' | 'medicines'
}

export default function InventoryUploader({ onUploadComplete, category }: InventoryUploaderProps) {
  const { accessToken } = useAuth()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedItems, setUploadedItems] = useState<InventoryItem[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const csvInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    setIsUploading(true)
    setUploadProgress(0)
    setErrors([])
    setUploadedItems([])

    try {
      const formData = new FormData()
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i])
      }
      formData.append('category', category)

      const response = await fetch('/api/inventory/upload', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const result = await response.json()
      setUploadedItems(result.items || [])
      setErrors(result.errors || [])
      
      if (result.items && result.items.length > 0) {
        toast.success(`Successfully uploaded ${result.items.length} items`)
        onUploadComplete()
      }
      
      if (result.errors && result.errors.length > 0) {
        toast.error(`${result.errors.length} items failed to upload`)
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
      setUploadProgress(100)
    }
  }

  const handleCSVUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setUploadProgress(0)
    setErrors([])
    setUploadedItems([])

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('category', category)

      const response = await fetch('/api/inventory/upload-csv', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error('CSV upload failed')
      }

      const result = await response.json()
      setUploadedItems(result.items || [])
      setErrors(result.errors || [])
      
      if (result.items && result.items.length > 0) {
        toast.success(`Successfully uploaded ${result.items.length} items from CSV`)
        onUploadComplete()
      }
      
      if (result.errors && result.errors.length > 0) {
        toast.error(`${result.errors.length} items failed to upload`)
      }
    } catch (error) {
      console.error('CSV upload error:', error)
      toast.error('CSV upload failed. Please check the file format.')
    } finally {
      setIsUploading(false)
      setUploadProgress(100)
    }
  }

  const downloadTemplate = () => {
    const template = category === 'spectacles' 
      ? 'name,brand,price,quantity,frame_material,frame_shape,lens_type,gender,age_group\nSample Spectacle,Brand Name,1500,10,Metal,Round,Single Vision,Unisex,Adult'
      : 'name,brand,price,quantity,dosage_form,strength,manufacturer,expiry_date\nSample Medicine,Brand Name,250,50,Tablet,500mg,Manufacturer,2025-12-31'
    
    const blob = new Blob([template], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${category}_template.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Upload {category.charAt(0).toUpperCase() + category.slice(1)}
        </h3>
        <button
          onClick={downloadTemplate}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <Download size={16} className="mr-2" />
          Download Template
        </button>
      </div>

      {/* Upload Methods */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* File Upload */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,.pdf,.doc,.docx"
            onChange={handleFileUpload}
            className="hidden"
          />
          <Upload size={48} className="mx-auto text-gray-400 mb-4" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">Upload Files</h4>
          <p className="text-sm text-gray-500 mb-4">
            Upload images, PDFs, or documents for {category}
          </p>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <Plus size={16} className="mr-2" />
            Select Files
          </button>
        </div>

        {/* CSV Upload */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-green-400 transition-colors">
          <input
            ref={csvInputRef}
            type="file"
            accept=".csv"
            onChange={handleCSVUpload}
            className="hidden"
          />
          <FileText size={48} className="mx-auto text-gray-400 mb-4" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">Upload CSV</h4>
          <p className="text-sm text-gray-500 mb-4">
            Upload CSV file with {category} data
          </p>
          <button
            onClick={() => csvInputRef.current?.click()}
            disabled={isUploading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
          >
            <FileText size={16} className="mr-2" />
            Select CSV
          </button>
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Uploading...</span>
            <span className="text-sm text-gray-500">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Results */}
      {uploadedItems.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <CheckCircle size={20} className="text-green-500 mr-2" />
            Successfully Uploaded ({uploadedItems.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {uploadedItems.map((item, index) => (
              <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h5 className="font-medium text-green-900">{item.name}</h5>
                <p className="text-sm text-green-700">
                  {item.brand && `${item.brand} • `}₹{item.price} • Qty: {item.quantity}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Errors */}
      {errors.length > 0 && (
        <div>
          <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <AlertCircle size={20} className="text-red-500 mr-2" />
            Upload Errors ({errors.length})
          </h4>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            {errors.map((error, index) => (
              <div key={index} className="text-sm text-red-700 mb-2">
                {error}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">Upload Instructions</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• For files: Upload images (JPG, PNG), PDFs, or documents</li>
          <li>• For CSV: Use the template format for proper data import</li>
          <li>• Maximum file size: 10MB per file</li>
          <li>• Supported formats: Images, PDF, DOC, DOCX, CSV</li>
        </ul>
      </div>
    </div>
  )
}
