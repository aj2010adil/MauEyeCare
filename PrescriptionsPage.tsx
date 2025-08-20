import { useEffect, useState } from 'react'
import { useAuth } from './AuthContext'
import { Plus, Search } from 'lucide-react'
import PrescriptionTable from './components/prescriptions/PrescriptionTable'

interface Patient {
  id: number
  first_name: string
  last_name?: string
}

interface Prescription {
  id: number
  created_at: string
  pdf_path?: string
  patient: Patient
}

export default function PrescriptionsPage() {
  const { accessToken } = useAuth()
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const load = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ page: page.toString(), q: searchQuery })
      const res = await fetch(`/api/prescriptions?${params.toString()}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      if (!res.ok) throw new Error('Failed to fetch prescriptions.')
      const data = await res.json()
      setPrescriptions(data.items)
      setTotalPages(Math.ceil(data.total / data.page_size))
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [page]) // Reload when page changes

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1) // Reset to first page on new search
    load()
  }

  return (
    <div className="p-4 md:p-6 space-y-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-800">Prescriptions</h1>
        <button className="bg-sky-600 text-white font-semibold rounded-lg px-4 py-2 flex items-center gap-2 hover:bg-sky-700 transition-colors">
          <Plus size={18} /> New Prescription
        </button>
      </div>

      <form onSubmit={handleSearch} className="flex items-center gap-2">
        <div className="relative flex-grow">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by patient name or phone..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
          />
        </div>
        <button type="submit" className="bg-gray-700 text-white font-semibold rounded-lg px-4 py-2 hover:bg-gray-800">Search</button>
      </form>

      <div>
        {isLoading && <div className="text-center p-8">Loading...</div>}
        {error && <div className="text-center p-8 text-red-500">{error}</div>}
        {!isLoading && !error && prescriptions.length === 0 && <div className="text-center p-8 text-gray-500">No prescriptions found.</div>}
        {!isLoading && !error && prescriptions.length > 0 && <PrescriptionTable prescriptions={prescriptions} />}
      </div>
    </div>
  )
}
