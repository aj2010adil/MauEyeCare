import { useEffect, useState } from 'react'
import { useAuth } from './AuthContext'

export default function Dashboard() {
  const { accessToken } = useAuth()
  const [data, setData] = useState<any | null>(null)
  useEffect(() => {
    fetch('/api/dashboard/stats', { headers: { Authorization: `Bearer ${accessToken}` } })
      .then(r => r.json()).then(setData).catch(() => setData(null))
  }, [accessToken])
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Dashboard</h2>
      {data ? (
        <div className="grid grid-cols-3 gap-4">
          <div className="border rounded p-4">Total Patients: <b>{data.total_patients}</b></div>
          <div className="border rounded p-4">Today Visits: <b>{data.today_visits}</b></div>
          <div className="border rounded p-4">Total Prescriptions: <b>{data.total_prescriptions}</b></div>
        </div>
      ) : (
        <div className="text-sm text-gray-500">Loading...</div>
      )}
    </div>
  )
}

