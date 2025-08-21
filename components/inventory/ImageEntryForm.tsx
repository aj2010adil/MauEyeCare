import React, { useState, useRef } from 'react'
import { Upload, Camera, Image as ImageIcon, Tag, X, RotateCcw, ZoomIn, ZoomOut, Download } from 'lucide-react'
import { useAuth } from '../../AuthContext'
import toast from 'react-hot-toast'

interface ProductTag {
  id: string
  name: string
  confidence: number
  category: string
}

interface ImageEntryFormProps {
  onClose: () => void
  onSave: (productData: ProductData) => void
  productType: 'spectacle' | 'medicine'
}

interface ProductData {
  name: string
  brand: string
  category: string
  description: string
  price: number
  quantity: number
  image_url: string
  tags: ProductTag[]
  specifications: Record<string, any>
}

export default function ImageEntryForm({ onClose, onSave, productType }: ImageEntryFormProps) {
  const { accessToken } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string>('')
  const [analyzedTags, setAnalyzedTags] = useState<ProductTag[]>([])
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [imageTransform, setImageTransform] = useState({
    rotation: 0,
    zoom: 1,
    brightness: 100,
    contrast: 100
  })

  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const [formData, setFormData] = useState({
    name: '',
    brand: '',
    category: '',
    description: '',
    price: 0,
    quantity: 1
  })

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      processImageFile(file)
    }
  }

  const processImageFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      toast.error('Please select a valid image file')
      return
    }

    setSelectedImage(file)
    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
      analyzeImage(file)
    }
    reader.readAsDataURL(file)
  }

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 }, 
          height: { ideal: 720 },
          facingMode: 'environment' // Use back camera if available
        } 
      })
      
      if (cameraRef.current) {
        cameraRef.current.srcObject = stream
        streamRef.current = stream
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      toast.error('Unable to access camera. Please check permissions.')
    }
  }

  const capturePhoto = () => {
    if (!cameraRef.current) return

    const canvas = document.createElement('canvas')
    const video = cameraRef.current
    const ctx = canvas.getContext('2d')

    if (!ctx) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0)

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'captured-photo.jpg', { type: 'image/jpeg' })
        processImageFile(file)
        stopCamera()
      }
    }, 'image/jpeg', 0.8)
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
  }

  const analyzeImage = async (file: File) => {
    setIsAnalyzing(true)
    
    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('product_type', productType)

      const response = await fetch('/api/inventory/analyze-image', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        body: formData
      })

      if (!response.ok) throw new Error('Analysis failed')

      const data = await response.json()
      setAnalyzedTags(data.tags || [])
      
      // Auto-fill form based on analysis
      if (data.suggestions) {
        setFormData(prev => ({
          ...prev,
          name: data.suggestions.name || prev.name,
          brand: data.suggestions.brand || prev.brand,
          category: data.suggestions.category || prev.category,
          description: data.suggestions.description || prev.description,
          price: data.suggestions.price || prev.price
        }))
      }

      toast.success('Image analyzed successfully!')
    } catch (error) {
      console.error('Error analyzing image:', error)
      toast.error('Failed to analyze image')
      
      // Fallback: generate mock tags for demo
      const mockTags = generateMockTags(productType)
      setAnalyzedTags(mockTags)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const generateMockTags = (type: 'spectacle' | 'medicine'): ProductTag[] => {
    if (type === 'spectacle') {
      return [
        { id: '1', name: 'Eyeglasses', confidence: 0.95, category: 'Product Type' },
        { id: '2', name: 'Ray-Ban', confidence: 0.87, category: 'Brand' },
        { id: '3', name: 'Aviator', confidence: 0.82, category: 'Style' },
        { id: '4', name: 'Metal Frame', confidence: 0.78, category: 'Material' },
        { id: '5', name: 'Sunglasses', confidence: 0.75, category: 'Type' }
      ]
    } else {
      return [
        { id: '1', name: 'Eye Drops', confidence: 0.92, category: 'Product Type' },
        { id: '2', name: 'Pharmaceutical', confidence: 0.88, category: 'Category' },
        { id: '3', name: 'Artificial Tears', confidence: 0.85, category: 'Product' },
        { id: '4', name: 'Lubricating', confidence: 0.79, category: 'Function' },
        { id: '5', name: 'Prescription', confidence: 0.72, category: 'Type' }
      ]
    }
  }

  const handleTagToggle = (tagId: string) => {
    setSelectedTags(prev => 
      prev.includes(tagId) 
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    )
  }

  const handleFormChange = (field: keyof typeof formData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    if (!selectedImage || !imagePreview) {
      toast.error('Please select an image first')
      return
    }

    if (!formData.name || !formData.brand) {
      toast.error('Please fill in required fields')
      return
    }

    setIsLoading(true)

    try {
      // Upload image
      const imageFormData = new FormData()
      imageFormData.append('file', selectedImage)
      imageFormData.append('product_type', productType)

      const uploadResponse = await fetch('/api/inventory/upload-image', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        body: imageFormData
      })

      if (!uploadResponse.ok) throw new Error('Image upload failed')

      const uploadData = await uploadResponse.json()
      const imageUrl = uploadData.image_url

      // Create product data
      const productData: ProductData = {
        ...formData,
        image_url: imageUrl,
        tags: analyzedTags.filter(tag => selectedTags.includes(tag.id)),
        specifications: {
          detected_tags: analyzedTags.map(tag => tag.name),
          image_analysis_confidence: analyzedTags.reduce((acc, tag) => acc + tag.confidence, 0) / analyzedTags.length
        }
      }

      onSave(productData)
      toast.success('Product saved successfully!')
      onClose()
    } catch (error) {
      console.error('Error saving product:', error)
      toast.error('Failed to save product')
    } finally {
      setIsLoading(false)
    }
  }

  const applyImageTransform = (transform: Partial<typeof imageTransform>) => {
    setImageTransform(prev => ({ ...prev, ...transform }))
  }

  const resetImageTransform = () => {
    setImageTransform({
      rotation: 0,
      zoom: 1,
      brightness: 100,
      contrast: 100
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <ImageIcon className="text-blue-600" size={24} />
            <div>
              <h2 className="text-xl font-bold text-gray-900">Add Product via Image</h2>
              <p className="text-sm text-gray-600">
                Upload or capture a photo to auto-detect product details
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex h-[calc(90vh-120px)]">
          {/* Left Panel - Image Upload/Preview */}
          <div className="flex-1 p-6 border-r border-gray-200">
            <div className="space-y-4">
              {/* Upload Methods */}
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center"
                >
                  <Upload className="mx-auto mb-2 text-gray-400" size={32} />
                  <div className="text-sm font-medium text-gray-700">Upload Image</div>
                  <div className="text-xs text-gray-500">JPG, PNG, WebP</div>
                </button>

                <button
                  onClick={startCamera}
                  className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center"
                >
                  <Camera className="mx-auto mb-2 text-gray-400" size={32} />
                  <div className="text-sm font-medium text-gray-700">Take Photo</div>
                  <div className="text-xs text-gray-500">Use camera</div>
                </button>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />

              {/* Camera View */}
              {streamRef.current && (
                <div className="relative bg-black rounded-lg overflow-hidden">
                  <video
                    ref={cameraRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-64 object-cover"
                  />
                  <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                    <button
                      onClick={capturePhoto}
                      className="p-3 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors"
                    >
                      <Camera size={24} className="text-gray-700" />
                    </button>
                  </div>
                </div>
              )}

              {/* Image Preview */}
              {imagePreview && (
                <div className="space-y-4">
                  <div className="relative bg-gray-100 rounded-lg overflow-hidden">
                    <img
                      src={imagePreview}
                      alt="Product preview"
                      className="w-full h-64 object-contain"
                      style={{
                        transform: `rotate(${imageTransform.rotation}deg) scale(${imageTransform.zoom})`,
                        filter: `brightness(${imageTransform.brightness}%) contrast(${imageTransform.contrast}%)`
                      }}
                    />
                    
                    {/* Image Controls */}
                    <div className="absolute top-2 right-2 bg-white rounded-lg shadow-lg p-2">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => applyImageTransform({ rotation: imageTransform.rotation - 90 })}
                          className="p-1 hover:bg-gray-100 rounded"
                        >
                          <RotateCcw size={16} />
                        </button>
                        <button
                          onClick={() => applyImageTransform({ zoom: Math.max(0.5, imageTransform.zoom - 0.1) })}
                          className="p-1 hover:bg-gray-100 rounded"
                        >
                          <ZoomOut size={16} />
                        </button>
                        <button
                          onClick={() => applyImageTransform({ zoom: Math.min(2, imageTransform.zoom + 0.1) })}
                          className="p-1 hover:bg-gray-100 rounded"
                        >
                          <ZoomIn size={16} />
                        </button>
                        <button
                          onClick={resetImageTransform}
                          className="p-1 hover:bg-gray-100 rounded text-xs"
                        >
                          Reset
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Image Adjustments */}
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Brightness: {imageTransform.brightness}%
                      </label>
                      <input
                        type="range"
                        min="50"
                        max="150"
                        value={imageTransform.brightness}
                        onChange={(e) => applyImageTransform({ brightness: parseInt(e.target.value) })}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Contrast: {imageTransform.contrast}%
                      </label>
                      <input
                        type="range"
                        min="50"
                        max="150"
                        value={imageTransform.contrast}
                        onChange={(e) => applyImageTransform({ contrast: parseInt(e.target.value) })}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Analysis Status */}
              {isAnalyzing && (
                <div className="flex items-center justify-center p-4 bg-blue-50 rounded-lg">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
                  <span className="text-blue-700">Analyzing image...</span>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Form & Tags */}
          <div className="w-96 p-6 overflow-y-auto">
            <div className="space-y-6">
              {/* Detected Tags */}
              {analyzedTags.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Tag size={16} />
                    Detected Tags
                  </h3>
                  <div className="space-y-2">
                    {analyzedTags.map(tag => (
                      <button
                        key={tag.id}
                        onClick={() => handleTagToggle(tag.id)}
                        className={`w-full p-2 rounded-lg border text-left transition-colors ${
                          selectedTags.includes(tag.id)
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">{tag.name}</div>
                            <div className="text-xs text-gray-500">{tag.category}</div>
                          </div>
                          <div className="text-xs text-gray-400">
                            {Math.round(tag.confidence * 100)}%
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Product Form */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Product Details</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Product Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleFormChange('name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter product name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Brand *
                  </label>
                  <input
                    type="text"
                    value={formData.brand}
                    onChange={(e) => handleFormChange('brand', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter brand name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => handleFormChange('category', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter category"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleFormChange('description', e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter product description"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Price (₹)
                    </label>
                    <input
                      type="number"
                      value={formData.price}
                      onChange={(e) => handleFormChange('price', parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0.00"
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Quantity
                    </label>
                    <input
                      type="number"
                      value={formData.quantity}
                      onChange={(e) => handleFormChange('quantity', parseInt(e.target.value) || 1)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="1"
                      min="1"
                    />
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3 pt-4">
                <button
                  onClick={handleSave}
                  disabled={isLoading || !selectedImage}
                  className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Saving...' : 'Save Product'}
                </button>
                
                <button
                  onClick={onClose}
                  className="w-full py-2 px-4 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
