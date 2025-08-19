import { useEffect, useState } from 'react'
import { useAuth } from './AuthContext'

export default function MarketingDashboard() {
  const { accessToken } = useAuth()
  const [rows, setRows] = useState<{ issue: string; count: number }[]>([])
  useEffect(() => {
    fetch('/api/dashboard/marketing', { headers: { Authorization: `Bearer ${accessToken}` } })
      .then(r => r.json()).then(d => setRows(d.top_issues || [])).catch(() => setRows([]))
  }, [accessToken])
  return (
    <div className="grid gap-3">
      <div className="text-xl font-semibold">Marketing Insights</div>
      <div className="grid gap-2">
        {rows.map((r, i) => (
          <div key={i} className="border rounded p-3 flex items-center">
            <div className="w-56">{r.issue}</div>
            <div className="h-3 bg-sky-200 rounded flex-1">
              <div className="h-3 bg-sky-600 rounded" style={{ width: Math.min(100, r.count * 10) + '%' }} />
            </div>
            <div className="w-10 text-right">{r.count}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

