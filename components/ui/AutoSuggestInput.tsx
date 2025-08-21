import React, { useState, useEffect, useRef } from 'react'
import { Search, ChevronDown, X } from 'lucide-react'

interface Suggestion {
  id: string | number
  label: string
  value: string
  description?: string
  category?: string
}

interface AutoSuggestInputProps {
  value: string
  onChange: (value: string) => void
  onSelect?: (suggestion: Suggestion) => void
  suggestions: Suggestion[]
  placeholder?: string
  label?: string
  error?: string
  disabled?: boolean
  loading?: boolean
  maxSuggestions?: number
  minChars?: number
  className?: string
  inputClassName?: string
  showClearButton?: boolean
  allowCustomValues?: boolean
}

export default function AutoSuggestInput({
  value,
  onChange,
  onSelect,
  suggestions,
  placeholder = 'Type to search...',
  label,
  error,
  disabled = false,
  loading = false,
  maxSuggestions = 10,
  minChars = 2,
  className = '',
  inputClassName = '',
  showClearButton = true,
  allowCustomValues = true
}: AutoSuggestInputProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [highlightedIndex, setHighlightedIndex] = useState(-1)
  const [inputValue, setInputValue] = useState(value)
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Filter suggestions based on input
  const filteredSuggestions = suggestions
    .filter(suggestion => 
      suggestion.label.toLowerCase().includes(inputValue.toLowerCase()) ||
      suggestion.description?.toLowerCase().includes(inputValue.toLowerCase())
    )
    .slice(0, maxSuggestions)

  // Show suggestions only if input has enough characters
  const shouldShowSuggestions = isOpen && 
    inputValue.length >= minChars && 
    filteredSuggestions.length > 0 &&
    !loading

  useEffect(() => {
    setInputValue(value)
  }, [value])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setHighlightedIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setInputValue(newValue)
    onChange(newValue)
    setIsOpen(true)
    setHighlightedIndex(-1)
  }

  const handleInputFocus = () => {
    if (inputValue.length >= minChars) {
      setIsOpen(true)
    }
  }

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!shouldShowSuggestions) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setHighlightedIndex(prev => 
          prev < filteredSuggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : -1)
        break
      case 'Enter':
        e.preventDefault()
        if (highlightedIndex >= 0) {
          handleSuggestionSelect(filteredSuggestions[highlightedIndex])
        } else if (allowCustomValues) {
          setIsOpen(false)
        }
        break
      case 'Escape':
        setIsOpen(false)
        setHighlightedIndex(-1)
        inputRef.current?.blur()
        break
    }
  }

  const handleSuggestionSelect = (suggestion: Suggestion) => {
    setInputValue(suggestion.label)
    onChange(suggestion.value)
    onSelect?.(suggestion)
    setIsOpen(false)
    setHighlightedIndex(-1)
  }

  const handleClear = () => {
    setInputValue('')
    onChange('')
    setIsOpen(false)
    setHighlightedIndex(-1)
    inputRef.current?.focus()
  }

  const highlightText = (text: string, query: string) => {
    if (!query) return text
    
    const regex = new RegExp(`(${query})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <span key={index} className="bg-yellow-200 font-semibold">
          {part}
        </span>
      ) : part
    )
  }

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}

      {/* Input Container */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleInputKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className={`
            w-full px-3 py-2 pr-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            ${error ? 'border-red-300' : 'border-gray-300'}
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
            ${inputClassName}
          `}
        />

        {/* Icons */}
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
          {loading && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          )}
          
          {showClearButton && inputValue && !disabled && (
            <button
              onClick={handleClear}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              type="button"
            >
              <X size={16} />
            </button>
          )}
          
          <ChevronDown 
            size={16} 
            className={`text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}

      {/* Suggestions Dropdown */}
      {shouldShowSuggestions && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          <div className="py-1">
            {filteredSuggestions.map((suggestion, index) => (
              <button
                key={suggestion.id}
                onClick={() => handleSuggestionSelect(suggestion)}
                className={`
                  w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none
                  ${index === highlightedIndex ? 'bg-blue-50 border-l-4 border-blue-500' : ''}
                `}
                type="button"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">
                      {highlightText(suggestion.label, inputValue)}
                    </div>
                    {suggestion.description && (
                      <div className="text-sm text-gray-500 mt-1">
                        {suggestion.description}
                      </div>
                    )}
                  </div>
                  {suggestion.category && (
                    <span className="ml-2 px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                      {suggestion.category}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
          
          {allowCustomValues && inputValue && !filteredSuggestions.some(s => s.label.toLowerCase() === inputValue.toLowerCase()) && (
            <div className="border-t border-gray-200 px-3 py-2 text-sm text-gray-500">
              Press Enter to use "{inputValue}"
            </div>
          )}
        </div>
      )}

      {/* No Results */}
      {isOpen && inputValue.length >= minChars && filteredSuggestions.length === 0 && !loading && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
          <div className="px-3 py-4 text-center text-gray-500">
            <Search size={20} className="mx-auto mb-2 text-gray-300" />
            <p>No suggestions found</p>
            {allowCustomValues && (
              <p className="text-sm mt-1">Press Enter to use custom value</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Specialized components for common use cases
export function PatientNameInput(props: Omit<AutoSuggestInputProps, 'suggestions'> & {
  patients: Array<{ id: number; first_name: string; last_name: string; phone?: string }>
}) {
  const suggestions: Suggestion[] = props.patients.map(patient => ({
    id: patient.id,
    label: `${patient.first_name} ${patient.last_name}`,
    value: `${patient.first_name} ${patient.last_name}`,
    description: patient.phone ? `📞 ${patient.phone}` : undefined,
    category: 'Patient'
  }))

  return <AutoSuggestInput {...props} suggestions={suggestions} />
}

export function DiagnosisInput(props: Omit<AutoSuggestInputProps, 'suggestions'>) {
  const commonDiagnoses: Suggestion[] = [
    { id: 'myopia', label: 'Myopia (Nearsightedness)', value: 'Myopia', category: 'Refractive Error' },
    { id: 'hyperopia', label: 'Hyperopia (Farsightedness)', value: 'Hyperopia', category: 'Refractive Error' },
    { id: 'astigmatism', label: 'Astigmatism', value: 'Astigmatism', category: 'Refractive Error' },
    { id: 'presbyopia', label: 'Presbyopia', value: 'Presbyopia', category: 'Age-related' },
    { id: 'cataract', label: 'Cataract', value: 'Cataract', category: 'Eye Disease' },
    { id: 'glaucoma', label: 'Glaucoma', value: 'Glaucoma', category: 'Eye Disease' },
    { id: 'diabetic_retinopathy', label: 'Diabetic Retinopathy', value: 'Diabetic Retinopathy', category: 'Eye Disease' },
    { id: 'dry_eye', label: 'Dry Eye Syndrome', value: 'Dry Eye Syndrome', category: 'Eye Condition' },
    { id: 'conjunctivitis', label: 'Conjunctivitis', value: 'Conjunctivitis', category: 'Eye Infection' },
    { id: 'normal', label: 'Normal Vision', value: 'Normal Vision', category: 'Normal' }
  ]

  return <AutoSuggestInput {...props} suggestions={commonDiagnoses} />
}

export function MedicineInput(props: Omit<AutoSuggestInputProps, 'suggestions'>) {
  const commonMedicines: Suggestion[] = [
    { id: 'tropicamide', label: 'Tropicamide 1%', value: 'Tropicamide 1%', description: 'Eye drops for pupil dilation', category: 'Dilation' },
    { id: 'cyclopentolate', label: 'Cyclopentolate 1%', value: 'Cyclopentolate 1%', description: 'Cycloplegic eye drops', category: 'Dilation' },
    { id: 'artificial_tears', label: 'Artificial Tears', value: 'Artificial Tears', description: 'Lubricating eye drops', category: 'Lubrication' },
    { id: 'antibiotic_drops', label: 'Antibiotic Eye Drops', value: 'Antibiotic Eye Drops', description: 'For bacterial infections', category: 'Antibiotic' },
    { id: 'antihistamine', label: 'Antihistamine Drops', value: 'Antihistamine Drops', description: 'For allergic reactions', category: 'Antihistamine' },
    { id: 'steroid_drops', label: 'Steroid Eye Drops', value: 'Steroid Eye Drops', description: 'For inflammation', category: 'Steroid' },
    { id: 'vitamin_a', label: 'Vitamin A Supplements', value: 'Vitamin A Supplements', description: 'For eye health', category: 'Vitamin' },
    { id: 'omega_3', label: 'Omega-3 Supplements', value: 'Omega-3 Supplements', description: 'For dry eye relief', category: 'Supplement' }
  ]

  return <AutoSuggestInput {...props} suggestions={commonMedicines} />
}

export function SpectacleBrandInput(props: Omit<AutoSuggestInputProps, 'suggestions'>) {
  const commonBrands: Suggestion[] = [
    { id: 'ray_ban', label: 'Ray-Ban', value: 'Ray-Ban', category: 'Premium' },
    { id: 'oakley', label: 'Oakley', value: 'Oakley', category: 'Premium' },
    { id: 'gucci', label: 'Gucci', value: 'Gucci', category: 'Luxury' },
    { id: 'prada', label: 'Prada', value: 'Prada', category: 'Luxury' },
    { id: 'titan', label: 'Titan', value: 'Titan', category: 'Indian' },
    { id: 'fastrack', label: 'Fastrack', value: 'Fastrack', category: 'Indian' },
    { id: 'vincent_chase', label: 'Vincent Chase', value: 'Vincent Chase', category: 'Indian' },
    { id: 'john_jacobs', label: 'John Jacobs', value: 'John Jacobs', category: 'Indian' },
    { id: 'lenskart', label: 'Lenskart', value: 'Lenskart', category: 'Indian' },
    { id: 'specsmakers', label: 'Specsmakers', value: 'Specsmakers', category: 'Indian' }
  ]

  return <AutoSuggestInput {...props} suggestions={commonBrands} />
}
