import { useEffect, useState } from 'react'
import { useAuth } from './AuthContext'

export default function OperationsDashboard() {
  const { accessToken } = useAuth()
  const [rows, setRows] = useState<any[]>([])
  useEffect(() => {
    fetch('/api/dashboard/operations', { headers: { Authorization: `Bearer ${accessToken}` } })
      .then(r => r.json()).then(d => setRows(d.today || [])).catch(() => setRows([]))
  }, [accessToken])
  return (
    <div className="grid gap-3">
      <div className="text-xl font-semibold">Today's Operations</div>
      <div className="grid gap-2">
        {rows.map(v => (
          <div key={v.id} className="border rounded p-3 flex gap-3">
            <div className="text-sm w-44">{new Date(v.time).toLocaleTimeString()}</div>
            <div className="flex-1">Patient #{v.patient_id}</div>
            <div className="text-sm text-gray-500">{v.issue}</div>
            <div className="text-sm">{v.advice}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

