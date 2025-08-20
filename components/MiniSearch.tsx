import React, { useEffect, useState } from 'react'
import { apiGet } from '../api'
import { useAuth } from '../AuthContext'

type Patient = { id: number, first_name: string, last_name?: string | null, phone?: string | null }

export default function MiniSearch({ onSelect }: { onSelect?: (p: Patient) => void }) {
  const { accessToken } = useAuth()
  const [q, setQ] = useState('')
  const [list, setList] = useState<Patient[]>([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const id = setTimeout(async () => {
      if (!q || q.length < 2) { setList([]); return }
      try {
        const data = await apiGet<Patient[]>(`/api/patients?q=${encodeURIComponent(q)}&page=1&page_size=10`, accessToken || undefined)
        setList(data)
        setOpen(true)
      } catch {
        setList([])
        setOpen(false)
      }
    }, 250)
    return () => clearTimeout(id)
  }, [q, accessToken])

  return (
    <div className="relative">
      <input
        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
        placeholder="Search patients by name or phone"
        value={q}
        onChange={e => setQ(e.target.value)}
        onFocus={() => setOpen(list.length > 0)}
      />
      {open && list.length > 0 && (
        <div className="absolute z-10 mt-1 max-h-64 w-full overflow-auto rounded-md border border-gray-200 bg-white shadow-lg">
          {list.map(p => (
            <button key={p.id} className="w-full text-left px-3 py-2 hover:bg-indigo-50"
              onClick={() => { setOpen(false); setQ(''); onSelect?.(p) }}>
              <div className="font-medium text-gray-900">{p.first_name} {p.last_name || ''}</div>
              {p.phone && <div className="text-xs text-gray-500">{p.phone}</div>}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}


