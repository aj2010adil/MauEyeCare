import { useEffect, useState } from 'react'
import { useAuth } from './AuthContext'

export default function PrescriptionsPage() {
  const { accessToken } = useAuth()
  const [patientId, setPatientId] = useState<number>(0)
  const [rows, setRows] = useState<any[]>([])
  const load = async () => {
    if (!patientId) return
    const res = await fetch(`/api/prescriptions/patient/${patientId}`, { headers: { Authorization: `Bearer ${accessToken}` } })
    setRows(await res.json())
  }
  useEffect(() => { if (patientId) load() }, [patientId])
  return (
    <div className="grid gap-3">
      <div className="text-xl font-semibold">Prescriptions</div>
      <div className="flex gap-2 items-center">
        <input className="border rounded p-2" placeholder="Patient ID" type="number" value={patientId} onChange={e => setPatientId(parseInt(e.target.value || '0'))} />
        <button className="border rounded px-3" onClick={load}>Load</button>
      </div>
      <div className="grid gap-2">
        {rows.map(p => (
          <div key={p.id} className="border rounded p-3 flex gap-3 items-center">
            <div className="flex-1">{new Date(p.created_at).toLocaleString()}</div>
            {p.pdf_path && <a className="text-sky-700 underline" href={`file:///${p.pdf_path.replace(/\\/g, '/')}`} target="_blank">Open PDF</a>}
          </div>
        ))}
      </div>
    </div>
  )
}

