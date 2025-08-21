import React, { useState } from 'react'
import { X, Star, Check, X as XIcon, ShoppingCart, Eye } from 'lucide-react'
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

interface SpectacleCompareProps {
  spectacles: Spectacle[]
  onClose: () => void
  onAddToCart: (spectacle: Spectacle) => void
  onTryOn: (spectacle: Spectacle) => void
  onRemoveFromCompare: (spectacleId: number) => void
}

export default function SpectacleCompare({ 
  spectacles, 
  onClose, 
  onAddToCart, 
  onTryOn, 
  onRemoveFromCompare 
}: SpectacleCompareProps) {
  const [selectedSpectacle, setSelectedSpectacle] = useState<Spectacle | null>(null)

  if (spectacles.length === 0) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Spectacles to Compare</h3>
            <p className="text-gray-600 mb-6">Add spectacles to your comparison list to see them side by side.</p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    )
  }

  const handleAddToCart = (spectacle: Spectacle) => {
    if (!spectacle.in_stock || spectacle.quantity === 0) {
      toast.error('This spectacle is out of stock')
      return
    }
    onAddToCart(spectacle)
    toast.success(`${spectacle.name} added to cart`)
  }

  const handleTryOn = (spectacle: Spectacle) => {
    onTryOn(spectacle)
  }

  const getSpecificationValue = (spectacle: Spectacle, key: string) => {
    if (spectacle.specifications && spectacle.specifications[key]) {
      return spectacle.specifications[key]
    }
    
    // Fallback to direct properties
    switch (key) {
      case 'frame_material': return spectacle.frame_material
      case 'frame_shape': return spectacle.frame_shape
      case 'lens_type': return spectacle.lens_type
      case 'gender': return spectacle.gender
      case 'age_group': return spectacle.age_group
      default: return 'N/A'
    }
  }

  const specificationKeys = [
    'frame_material',
    'frame_shape', 
    'lens_type',
    'gender',
    'age_group',
    'weight',
    'dimensions',
    'coating',
    'uv_protection',
    'anti_reflective',
    'scratch_resistant'
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Compare Spectacles</h2>
            <p className="text-gray-600">Side-by-side comparison of {spectacles.length} spectacles</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Comparison Table */}
        <div className="overflow-auto max-h-[calc(90vh-120px)]">
          <div className="min-w-full">
            {/* Spectacle Headers */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6 bg-gray-50">
              {spectacles.map((spectacle, index) => (
                <div key={spectacle.id} className="text-center">
                  <div className="relative">
                    <button
                      onClick={() => onRemoveFromCompare(spectacle.id)}
                      className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                      title="Remove from comparison"
                    >
                      <XIcon size={12} />
                    </button>
                    <img
                      src={spectacle.image_url || '/placeholder-spectacle.jpg'}
                      alt={spectacle.name}
                      className="w-32 h-32 object-cover rounded-lg mx-auto mb-4 border-2 border-gray-200"
                    />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1">{spectacle.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{spectacle.brand}</p>
                  <p className="text-lg font-bold text-blue-600 mb-3">₹{spectacle.price.toLocaleString()}</p>
                  
                  {/* Action Buttons */}
                  <div className="flex items-center justify-center gap-2 mb-3">
                    <button
                      onClick={() => handleTryOn(spectacle)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                      title="Try On"
                    >
                      <Eye size={16} />
                    </button>
                    <button
                      onClick={() => handleAddToCart(spectacle)}
                      disabled={!spectacle.in_stock || spectacle.quantity === 0}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-full transition-colors disabled:opacity-50"
                      title="Add to Cart"
                    >
                      <ShoppingCart size={16} />
                    </button>
                  </div>

                  {/* Stock Status */}
                  <div className={`text-sm px-2 py-1 rounded-full ${
                    spectacle.in_stock && spectacle.quantity > 0 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {spectacle.in_stock && spectacle.quantity > 0 
                      ? `In Stock (${spectacle.quantity})` 
                      : 'Out of Stock'
                    }
                  </div>
                </div>
              ))}
            </div>

            {/* Specifications Comparison */}
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Specifications</h3>
              
              {specificationKeys.map(specKey => {
                const values = spectacles.map(s => getSpecificationValue(s, specKey))
                const allSame = values.every(v => v === values[0])
                
                return (
                  <div key={specKey} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 py-3 border-b border-gray-100">
                    <div className="font-medium text-gray-700 capitalize">
                      {specKey.replace(/_/g, ' ')}
                    </div>
                    {spectacles.map((spectacle, index) => (
                      <div key={`${spectacle.id}-${specKey}`} className="text-center">
                        <span className={`text-sm ${
                          allSame ? 'text-green-600' : 'text-gray-900'
                        }`}>
                          {values[index]}
                        </span>
                        {allSame && values[0] !== 'N/A' && (
                          <Check size={14} className="inline ml-1 text-green-600" />
                        )}
                      </div>
                    ))}
                  </div>
                )
              })}

              {/* Description */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 py-3 border-b border-gray-100">
                <div className="font-medium text-gray-700">Description</div>
                {spectacles.map(spectacle => (
                  <div key={`${spectacle.id}-description`} className="text-center">
                    <p className="text-sm text-gray-600 line-clamp-3">
                      {spectacle.description || 'No description available'}
                    </p>
                  </div>
                ))}
              </div>

              {/* Ratings */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 py-3">
                <div className="font-medium text-gray-700">Rating</div>
                {spectacles.map(spectacle => (
                  <div key={`${spectacle.id}-rating`} className="text-center">
                    <div className="flex items-center justify-center gap-1">
                      <Star size={14} className="text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600">4.5</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600">
              {spectacles.length} spectacles selected for comparison
            </p>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Close Comparison
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
