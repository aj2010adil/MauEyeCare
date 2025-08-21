import React, { useState, useEffect } from 'react'
import { Eye, GitCompare, Camera, Filter, Search, Star, Heart, ShoppingCart } from 'lucide-react'
import SpectacleShowcase from './components/spectacles/SpectacleShowcase'
import SpectacleCompare from './components/spectacles/SpectacleCompare'
import TryOn3DViewer from './components/spectacles/TryOn3DViewer'
import AutoSuggestInput from './components/ui/AutoSuggestInput'
import Pagination from './components/ui/Pagination'
import { apiGet } from './api'
import { useAuth } from './AuthContext'

interface Spectacle {
  id: number
  name: string
  brand: string
  price: number
  image_url: string
  frame_material: string
  frame_shape: string
  lens_type: string
  gender: string
  age_group: string
  description: string
  specifications: any
  in_stock: boolean
  quantity: number
}

interface ShowcaseFilters {
  search: string
  brand: string
  frame_shape: string
  gender: string
  min_price: number | null
  max_price: number | null
  in_stock: boolean
}

const ShowcasePage: React.FC = () => {
  const { accessToken } = useAuth()
  const [spectacles, setSpectacles] = useState<Spectacle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const [selectedSpectacles, setSelectedSpectacles] = useState<Spectacle[]>([])
  const [showCompare, setShowCompare] = useState(false)
  const [showTryOn, setShowTryOn] = useState(false)
  const [selectedForTryOn, setSelectedForTryOn] = useState<Spectacle | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'showcase'>('showcase')
  const [filters, setFilters] = useState<ShowcaseFilters>({
    search: '',
    brand: '',
    frame_shape: '',
    gender: '',
    min_price: null,
    max_price: null,
    in_stock: true // Default to showing only in-stock items
  })

  const pageSize = 12

  const fetchSpectacles = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        skip: ((currentPage - 1) * pageSize).toString(),
        limit: pageSize.toString()
      })

      // Add filters to params
      if (filters.search) params.append('search', filters.search)
      if (filters.brand) params.append('brand', filters.brand)
      if (filters.frame_shape) params.append('frame_shape', filters.frame_shape)
      if (filters.gender) params.append('gender', filters.gender)
      if (filters.min_price !== null) params.append('min_price', filters.min_price.toString())
      if (filters.max_price !== null) params.append('max_price', filters.max_price.toString())
      if (filters.in_stock !== null) params.append('in_stock', filters.in_stock.toString())

      const response = await apiGet<{items: Spectacle[], total: number}>(`/api/inventory/spectacles?${params}`, accessToken || undefined)
      setSpectacles(response.items)
      setTotalItems(response.total)
      setTotalPages(Math.ceil(response.total / pageSize))
      setError(null)
    } catch (err) {
      setError('Failed to fetch spectacles')
      console.error('Error fetching spectacles:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSpectacles()
  }, [currentPage, filters])

  const handleFilterChange = (key: keyof ShowcaseFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setCurrentPage(1)
  }

  const clearFilters = () => {
    setFilters({
      search: '',
      brand: '',
      frame_shape: '',
      gender: '',
      min_price: null,
      max_price: null,
      in_stock: true
    })
    setCurrentPage(1)
  }

  const handleSelectForCompare = (spectacle: Spectacle) => {
    if (selectedSpectacles.find(s => s.id === spectacle.id)) {
      setSelectedSpectacles(prev => prev.filter(s => s.id !== spectacle.id))
    } else if (selectedSpectacles.length < 3) {
      setSelectedSpectacles(prev => [...prev, spectacle])
    }
  }

  const handleTryOn = (spectacle: Spectacle) => {
    setSelectedForTryOn(spectacle)
    setShowTryOn(true)
  }

  const handleCompare = () => {
    if (selectedSpectacles.length >= 2) {
      setShowCompare(true)
    }
  }

  if (loading && spectacles.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Spectacle Showcase</h1>
          <p className="text-gray-600">Browse, compare, and try on spectacles virtually</p>
        </div>
        <div className="flex items-center space-x-3">
          {selectedSpectacles.length > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">
                {selectedSpectacles.length} selected
              </span>
              <button
                onClick={handleCompare}
                disabled={selectedSpectacles.length < 2}
                className="flex items-center px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <GitCompare className="w-4 h-4 mr-2" />
                Compare
              </button>
            </div>
          )}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('showcase')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'showcase'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Showcase
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'grid'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Grid
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Filters</h3>
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            Clear All
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Search spectacles..."
                className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
            <AutoSuggestInput
              value={filters.brand}
              onChange={(value) => handleFilterChange('brand', value)}
              placeholder="Select brand..."
              suggestions={[
                { id: 'ray-ban', label: 'Ray-Ban', value: 'Ray-Ban' },
                { id: 'oakley', label: 'Oakley', value: 'Oakley' },
                { id: 'prada', label: 'Prada', value: 'Prada' },
                { id: 'gucci', label: 'Gucci', value: 'Gucci' },
                { id: 'tom-ford', label: 'Tom Ford', value: 'Tom Ford' }
              ]}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Frame Shape</label>
            <select
              value={filters.frame_shape}
              onChange={(e) => handleFilterChange('frame_shape', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Shapes</option>
              <option value="aviator">Aviator</option>
              <option value="wayfarer">Wayfarer</option>
              <option value="round">Round</option>
              <option value="square">Square</option>
              <option value="cat-eye">Cat Eye</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
            <select
              value={filters.gender}
              onChange={(e) => handleFilterChange('gender', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Genders</option>
              <option value="men">Men</option>
              <option value="women">Women</option>
              <option value="unisex">Unisex</option>
              <option value="kids">Kids</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min Price</label>
            <input
              type="number"
              value={filters.min_price || ''}
              onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : null)}
              placeholder="₹0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Price</label>
            <input
              type="number"
              value={filters.max_price || ''}
              onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : null)}
              placeholder="₹50000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">
              Available Spectacles ({totalItems} items)
            </h3>
            <div className="text-sm text-gray-500">
              Page {currentPage} of {totalPages}
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-400">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {spectacles.length === 0 && !loading ? (
          <div className="p-12 text-center">
            <div className="text-gray-400 mb-4">
              <Eye className="w-12 h-12 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No spectacles found</h3>
            <p className="text-gray-500 mb-4">Try adjusting your filters to see more options.</p>
          </div>
        ) : viewMode === 'showcase' ? (
          <SpectacleShowcase
            spectacles={spectacles}
            onSelectForCompare={handleSelectForCompare}
            onTryOn={handleTryOn}
            selectedSpectacles={selectedSpectacles}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-6">
            {spectacles.map((spectacle) => (
              <div key={spectacle.id} className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-square bg-gray-100 relative group">
                  {spectacle.image_url ? (
                    <img
                      src={spectacle.image_url}
                      alt={spectacle.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <Eye className="w-12 h-12" />
                    </div>
                  )}
                  
                  {/* Overlay Actions */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleTryOn(spectacle)}
                        className="p-2 bg-white rounded-full text-gray-700 hover:bg-gray-100 transition-colors"
                        title="Try On"
                      >
                        <Camera className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleSelectForCompare(spectacle)}
                        className={`p-2 rounded-full transition-colors ${
                          selectedSpectacles.find(s => s.id === spectacle.id)
                            ? 'bg-purple-600 text-white'
                            : 'bg-white text-gray-700 hover:bg-gray-100'
                        }`}
                        title="Compare"
                      >
                        <GitCompare className="w-4 h-4" />
                      </button>
                      <button
                        className="p-2 bg-white rounded-full text-gray-700 hover:bg-gray-100 transition-colors"
                        title="Add to Wishlist"
                      >
                        <Heart className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Price Badge */}
                  <div className="absolute top-2 left-2">
                    <span className="px-2 py-1 bg-blue-600 text-white text-xs font-medium rounded-full">
                      ₹{spectacle.price.toLocaleString()}
                    </span>
                  </div>

                  {/* Stock Status */}
                  <div className="absolute top-2 right-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      spectacle.in_stock 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {spectacle.in_stock ? 'In Stock' : 'Out of Stock'}
                    </span>
                  </div>
                </div>

                <div className="p-4">
                  <h4 className="font-semibold text-gray-900 mb-1">{spectacle.name}</h4>
                  <p className="text-sm text-gray-600 mb-2">{spectacle.brand}</p>
                  
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-3 h-3 text-yellow-400 fill-current" />
                      ))}
                      <span className="text-xs text-gray-500 ml-1">(4.5)</span>
                    </div>
                    <span className="text-sm text-gray-500">Qty: {spectacle.quantity}</span>
                  </div>

                  <div className="text-xs text-gray-500 space-y-1 mb-3">
                    <div className="flex justify-between">
                      <span>Shape:</span>
                      <span className="font-medium">{spectacle.frame_shape}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Material:</span>
                      <span className="font-medium">{spectacle.frame_material}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Gender:</span>
                      <span className="font-medium">{spectacle.gender}</span>
                    </div>
                  </div>

                  <button
                    disabled={!spectacle.in_stock}
                    className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    {spectacle.in_stock ? 'Add to Cart' : 'Out of Stock'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {totalPages > 1 && (
          <div className="p-6 border-t">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          </div>
        )}
      </div>

      {/* Modals */}
      {showCompare && selectedSpectacles.length >= 2 && (
        <SpectacleCompare
          spectacles={selectedSpectacles}
          onClose={() => setShowCompare(false)}
        />
      )}

      {showTryOn && selectedForTryOn && (
        <TryOn3DViewer
          spectacle={selectedForTryOn}
          onClose={() => {
            setShowTryOn(false)
            setSelectedForTryOn(null)
          }}
        />
      )}
    </div>
  )
}

export default ShowcasePage
