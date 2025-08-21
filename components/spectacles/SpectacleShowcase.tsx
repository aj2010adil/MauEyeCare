import React, { useState, useEffect } from 'react'
import { Search, Filter, Grid, List, Heart, ShoppingCart, Eye, Compare, Star } from 'lucide-react'
import { useAuth } from '../../AuthContext'
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

interface SpectacleShowcaseProps {
  onAddToCart: (spectacle: Spectacle) => void
  onTryOn: (spectacle: Spectacle) => void
  onCompare: (spectacle: Spectacle) => void
}

export default function SpectacleShowcase({ onAddToCart, onTryOn, onCompare }: SpectacleShowcaseProps) {
  const { accessToken } = useAuth()
  const [spectacles, setSpectacles] = useState<Spectacle[]>([])
  const [filteredSpectacles, setFilteredSpectacles] = useState<Spectacle[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFilters, setSelectedFilters] = useState({
    brand: '',
    frame_shape: '',
    lens_type: '',
    gender: '',
    price_range: '',
    in_stock: false
  })

  // Load spectacles
  useEffect(() => {
    loadSpectacles()
  }, [])

  // Apply filters
  useEffect(() => {
    applyFilters()
  }, [spectacles, searchQuery, selectedFilters])

  const loadSpectacles = async () => {
    try {
      const response = await fetch('/api/inventory/spectacles', {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      
      if (!response.ok) throw new Error('Failed to load spectacles')
      
      const data = await response.json()
      setSpectacles(data.items || data)
    } catch (error) {
      console.error('Error loading spectacles:', error)
      toast.error('Failed to load spectacles')
    } finally {
      setIsLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...spectacles]

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(spectacle =>
        spectacle.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        spectacle.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
        spectacle.description?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Brand filter
    if (selectedFilters.brand) {
      filtered = filtered.filter(spectacle => spectacle.brand === selectedFilters.brand)
    }

    // Frame shape filter
    if (selectedFilters.frame_shape) {
      filtered = filtered.filter(spectacle => spectacle.frame_shape === selectedFilters.frame_shape)
    }

    // Lens type filter
    if (selectedFilters.lens_type) {
      filtered = filtered.filter(spectacle => spectacle.lens_type === selectedFilters.lens_type)
    }

    // Gender filter
    if (selectedFilters.gender) {
      filtered = filtered.filter(spectacle => spectacle.gender === selectedFilters.gender)
    }

    // Price range filter
    if (selectedFilters.price_range) {
      const [min, max] = selectedFilters.price_range.split('-').map(Number)
      filtered = filtered.filter(spectacle => {
        if (max) {
          return spectacle.price >= min && spectacle.price <= max
        } else {
          return spectacle.price >= min
        }
      })
    }

    // Stock filter
    if (selectedFilters.in_stock) {
      filtered = filtered.filter(spectacle => spectacle.in_stock && spectacle.quantity > 0)
    }

    setFilteredSpectacles(filtered)
  }

  const getUniqueValues = (field: keyof Spectacle) => {
    return [...new Set(spectacles.map(s => s[field]).filter(Boolean))]
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

  const handleCompare = (spectacle: Spectacle) => {
    onCompare(spectacle)
    toast.success(`${spectacle.name} added to comparison`)
  }

  const clearFilters = () => {
    setSearchQuery('')
    setSelectedFilters({
      brand: '',
      frame_shape: '',
      lens_type: '',
      gender: '',
      price_range: '',
      in_stock: false
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading spectacles...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Spectacle Collection</h2>
          <p className="text-gray-600">Discover our premium collection of eyewear</p>
        </div>
        
        {/* View Mode Toggle */}
        <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'grid' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Grid size={20} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'list' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <List size={20} />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search spectacles by name, brand, or description..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {/* Brand Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
            <select
              value={selectedFilters.brand}
              onChange={(e) => setSelectedFilters(prev => ({ ...prev, brand: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Brands</option>
              {getUniqueValues('brand').map(brand => (
                <option key={brand} value={brand}>{brand}</option>
              ))}
            </select>
          </div>

          {/* Frame Shape Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Frame Shape</label>
            <select
              value={selectedFilters.frame_shape}
              onChange={(e) => setSelectedFilters(prev => ({ ...prev, frame_shape: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Shapes</option>
              {getUniqueValues('frame_shape').map(shape => (
                <option key={shape} value={shape}>{shape}</option>
              ))}
            </select>
          </div>

          {/* Lens Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Lens Type</label>
            <select
              value={selectedFilters.lens_type}
              onChange={(e) => setSelectedFilters(prev => ({ ...prev, lens_type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Types</option>
              {getUniqueValues('lens_type').map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          {/* Gender Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
            <select
              value={selectedFilters.gender}
              onChange={(e) => setSelectedFilters(prev => ({ ...prev, gender: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All</option>
              {getUniqueValues('gender').map(gender => (
                <option key={gender} value={gender}>{gender}</option>
              ))}
            </select>
          </div>

          {/* Price Range Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Price Range</label>
            <select
              value={selectedFilters.price_range}
              onChange={(e) => setSelectedFilters(prev => ({ ...prev, price_range: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Prices</option>
              <option value="0-1000">Under ₹1,000</option>
              <option value="1000-3000">₹1,000 - ₹3,000</option>
              <option value="3000-5000">₹3,000 - ₹5,000</option>
              <option value="5000-">Above ₹5,000</option>
            </select>
          </div>

          {/* Stock Filter */}
          <div className="flex items-center">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={selectedFilters.in_stock}
                onChange={(e) => setSelectedFilters(prev => ({ ...prev, in_stock: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">In Stock Only</span>
            </label>
          </div>
        </div>

        {/* Clear Filters */}
        <div className="mt-4 flex justify-between items-center">
          <span className="text-sm text-gray-600">
            {filteredSpectacles.length} of {spectacles.length} spectacles
          </span>
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Clear all filters
          </button>
        </div>
      </div>

      {/* Spectacles Grid/List */}
      {filteredSpectacles.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Search className="text-gray-400" size={32} />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No spectacles found</h3>
          <p className="text-gray-500">Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
          : 'space-y-4'
        }>
          {filteredSpectacles.map(spectacle => (
            <SpectacleCard
              key={spectacle.id}
              spectacle={spectacle}
              viewMode={viewMode}
              onAddToCart={handleAddToCart}
              onTryOn={handleTryOn}
              onCompare={handleCompare}
            />
          ))}
        </div>
      )}
    </div>
  )
}

interface SpectacleCardProps {
  spectacle: Spectacle
  viewMode: 'grid' | 'list'
  onAddToCart: (spectacle: Spectacle) => void
  onTryOn: (spectacle: Spectacle) => void
  onCompare: (spectacle: Spectacle) => void
}

function SpectacleCard({ spectacle, viewMode, onAddToCart, onTryOn, onCompare }: SpectacleCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  if (viewMode === 'list') {
    return (
      <div 
        className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="flex items-center gap-4">
          {/* Image */}
          <div className="flex-shrink-0">
            <img
              src={spectacle.image_url || '/placeholder-spectacle.jpg'}
              alt={spectacle.name}
              className="w-20 h-20 object-cover rounded-lg"
            />
          </div>

          {/* Details */}
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 truncate">{spectacle.name}</h3>
            <p className="text-sm text-gray-600">{spectacle.brand}</p>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
              <span>{spectacle.frame_shape} • {spectacle.lens_type}</span>
              <span>{spectacle.gender} • {spectacle.age_group}</span>
            </div>
          </div>

          {/* Price and Actions */}
          <div className="flex flex-col items-end gap-2">
            <div className="text-right">
              <p className="text-xl font-bold text-gray-900">₹{spectacle.price.toLocaleString()}</p>
              <p className={`text-sm ${spectacle.in_stock && spectacle.quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {spectacle.in_stock && spectacle.quantity > 0 ? `In Stock (${spectacle.quantity})` : 'Out of Stock'}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => onTryOn(spectacle)}
                className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                title="Try On"
              >
                <Eye size={16} />
              </button>
              <button
                onClick={() => onCompare(spectacle)}
                className="p-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-full transition-colors"
                title="Compare"
              >
                <Compare size={16} />
              </button>
              <button
                onClick={() => onAddToCart(spectacle)}
                disabled={!spectacle.in_stock || spectacle.quantity === 0}
                className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-full transition-colors disabled:opacity-50"
                title="Add to Cart"
              >
                <ShoppingCart size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div 
      className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Image */}
      <div className="relative aspect-square bg-gray-100">
        <img
          src={spectacle.image_url || '/placeholder-spectacle.jpg'}
          alt={spectacle.name}
          className="w-full h-full object-cover"
        />
        
        {/* Overlay Actions */}
        {isHovered && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center gap-2">
            <button
              onClick={() => onTryOn(spectacle)}
              className="p-3 bg-white text-gray-900 rounded-full hover:bg-blue-50 transition-colors"
              title="Try On"
            >
              <Eye size={20} />
            </button>
            <button
              onClick={() => onCompare(spectacle)}
              className="p-3 bg-white text-gray-900 rounded-full hover:bg-purple-50 transition-colors"
              title="Compare"
            >
              <Compare size={20} />
            </button>
            <button
              onClick={() => onAddToCart(spectacle)}
              disabled={!spectacle.in_stock || spectacle.quantity === 0}
              className="p-3 bg-white text-gray-900 rounded-full hover:bg-green-50 transition-colors disabled:opacity-50"
              title="Add to Cart"
            >
              <ShoppingCart size={20} />
            </button>
          </div>
        )}

        {/* Stock Badge */}
        {!spectacle.in_stock || spectacle.quantity === 0 ? (
          <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
            Out of Stock
          </div>
        ) : (
          <div className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
            In Stock
          </div>
        )}
      </div>

      {/* Details */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 mb-1 truncate">{spectacle.name}</h3>
        <p className="text-sm text-gray-600 mb-2">{spectacle.brand}</p>
        
        <div className="flex items-center justify-between mb-2">
          <span className="text-lg font-bold text-gray-900">₹{spectacle.price.toLocaleString()}</span>
          <div className="flex items-center gap-1">
            <Star size={14} className="text-yellow-400 fill-current" />
            <span className="text-sm text-gray-600">4.5</span>
          </div>
        </div>

        <div className="text-xs text-gray-500 space-y-1">
          <p>{spectacle.frame_shape} • {spectacle.lens_type}</p>
          <p>{spectacle.gender} • {spectacle.age_group}</p>
        </div>
      </div>
    </div>
  )
}
