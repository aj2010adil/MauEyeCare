import React, { useState } from 'react'
import { Eye, ShoppingCart, Compare, Camera, Upload, Plus } from 'lucide-react'
import SpectacleShowcase from './components/spectacles/SpectacleShowcase'
import SpectacleCompare from './components/spectacles/SpectacleCompare'
import TryOn3DViewer from './components/spectacles/TryOn3DViewer'
import InventoryUploader from './components/inventory/InventoryUploader'
import ImageEntryForm from './components/inventory/ImageEntryForm'
import toast from 'react-hot-toast'

interface Spectacle {
  id: number
  name: string
  brand: string
  price: number
  image_url?: string
  frame_material: string
  frame_shape: string
  lens_type: string
  gender: string
  age_group: string
  description?: string
  specifications?: Record<string, any>
  in_stock: boolean
  quantity: number
}

export default function ShowcasePage() {
  const [compareList, setCompareList] = useState<Spectacle[]>([])
  const [showCompare, setShowCompare] = useState(false)
  const [showTryOn, setShowTryOn] = useState(false)
  const [selectedSpectacle, setSelectedSpectacle] = useState<Spectacle | null>(null)
  const [showInventoryUploader, setShowInventoryUploader] = useState(false)
  const [showImageEntry, setShowImageEntry] = useState(false)
  const [cart, setCart] = useState<Spectacle[]>([])

  const handleAddToCart = (spectacle: Spectacle) => {
    setCart(prev => [...prev, spectacle])
    toast.success(`${spectacle.name} added to cart`)
  }

  const handleTryOn = (spectacle: Spectacle) => {
    setSelectedSpectacle(spectacle)
    setShowTryOn(true)
  }

  const handleCompare = (spectacle: Spectacle) => {
    if (compareList.find(s => s.id === spectacle.id)) {
      toast.error('Spectacle already in comparison list')
      return
    }
    
    if (compareList.length >= 3) {
      toast.error('Maximum 3 spectacles can be compared')
      return
    }
    
    setCompareList(prev => [...prev, spectacle])
    toast.success(`${spectacle.name} added to comparison`)
  }

  const handleRemoveFromCompare = (spectacleId: number) => {
    setCompareList(prev => prev.filter(s => s.id !== spectacleId))
  }

  const handleCaptureImage = (imageData: string) => {
    // Handle captured image from try-on
    console.log('Captured image:', imageData)
    toast.success('Image captured successfully!')
  }

  const handleSaveProduct = (productData: any) => {
    // Handle saving product from image entry
    console.log('Product saved:', productData)
    toast.success('Product saved successfully!')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Spectacle Showcase</h1>
              <p className="text-gray-600">Browse, compare, and try on spectacles</p>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Compare Button */}
              {compareList.length > 0 && (
                <button
                  onClick={() => setShowCompare(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <Compare size={20} />
                  Compare ({compareList.length})
                </button>
              )}
              
              {/* Cart Button */}
              {cart.length > 0 && (
                <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  <ShoppingCart size={20} />
                  Cart ({cart.length})
                </button>
              )}
              
              {/* Add Inventory Button */}
              <button
                onClick={() => setShowInventoryUploader(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Upload size={20} />
                Upload Inventory
              </button>
              
              {/* Add via Image Button */}
              <button
                onClick={() => setShowImageEntry(true)}
                className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
              >
                <Camera size={20} />
                Add via Image
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <SpectacleShowcase
          onAddToCart={handleAddToCart}
          onTryOn={handleTryOn}
          onCompare={handleCompare}
        />
      </div>

      {/* Comparison Modal */}
      {showCompare && (
        <SpectacleCompare
          spectacles={compareList}
          onClose={() => setShowCompare(false)}
          onAddToCart={handleAddToCart}
          onTryOn={handleTryOn}
          onRemoveFromCompare={handleRemoveFromCompare}
        />
      )}

      {/* Try-On Modal */}
      {showTryOn && selectedSpectacle && (
        <TryOn3DViewer
          spectacle={selectedSpectacle}
          onClose={() => setShowTryOn(false)}
          onCapture={handleCaptureImage}
          onAddToCart={handleAddToCart}
        />
      )}

      {/* Inventory Uploader Modal */}
      {showInventoryUploader && (
        <InventoryUploader
          onClose={() => setShowInventoryUploader(false)}
          onUploadComplete={(results) => {
            console.log('Upload results:', results)
            toast.success('Inventory uploaded successfully!')
            setShowInventoryUploader(false)
          }}
        />
      )}

      {/* Image Entry Modal */}
      {showImageEntry && (
        <ImageEntryForm
          onClose={() => setShowImageEntry(false)}
          onSave={handleSaveProduct}
          productType="spectacle"
        />
      )}
    </div>
  )
}
