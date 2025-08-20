import { useEffect, useMemo, useState } from 'react'
import { useAuth } from './AuthContext'
import KPICard from './components/KPICard'
import MiniSearch from './components/MiniSearch'

export default function Dashboard() {
  const { accessToken } = useAuth()
  const authHeader = useMemo(() => ({ Authorization: `Bearer ${accessToken}` }), [accessToken])

  const [stats, setStats] = useState<any | null>(null)
  const [ops, setOps] = useState<{ today: { id: number, patient_id: number, time: string, issue?: string }[] } | null>(null)
  const [lab, setLab] = useState<any[] | null>(null)
  const [posToday, setPosToday] = useState<{ total: number, orders: number } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    async function load() {
      setLoading(true)
      try {
        const [s, o, l, p] = await Promise.all([
          fetch('/api/dashboard/stats', { headers: authHeader }).then(r => r.json()),
          fetch('/api/dashboard/operations', { headers: authHeader }).then(r => r.json()),
          fetch('/api/lab/jobs', { headers: authHeader }).then(r => r.json()),
          fetch('/api/dashboard/pos-summary', { headers: authHeader }).then(r => r.json()).catch(() => ({ total_today: 0, orders_today: 0 })),
        ])
        if (!alive) return
        setStats(s)
        setOps(o)
        setLab(l)
        setPosToday({ total: p.total_today ?? 0, orders: p.orders_today ?? 0 })
      } catch {
        if (!alive) return
        setStats(null); setOps(null); setLab(null)
      } finally { if (alive) setLoading(false) }
    }
    load()
    return () => { alive = false }
  }, [authHeader])

  const today = new Date().toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })

  return (
    <div className="p-2 sm:p-4 md:p-6">
      <div className="flex flex-col md:flex-row md:items-center gap-3 mb-4">
        <div className="text-2xl font-semibold tracking-tight text-gray-900">Today · {today}</div>
        <div className="md:flex-1"><MiniSearch /></div>
        <div className="flex gap-2">
          <a href="/visits/new" className="inline-flex items-center rounded-lg bg-indigo-600 text-white px-3 py-2 hover:bg-indigo-700">Start Consultation</a>
          <a href="/prescriptions" className="inline-flex items-center rounded-lg border border-indigo-600 text-indigo-700 px-3 py-2 hover:bg-indigo-50">New Prescription</a>
        </div>
      </div>

      {loading && <div className="text-sm text-gray-500">Loading...</div>}

      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <KPICard title="Patients Today" value={stats?.today_visits ?? 0} accent="blue" />
          <KPICard title="Total Patients" value={stats?.total_patients ?? 0} accent="indigo" />
          <KPICard title="Prescriptions" value={stats?.total_prescriptions ?? 0} accent="green" />
          <KPICard title="Revenue Today" value={(posToday?.total ?? 0).toLocaleString()} subtitle={`${posToday?.orders ?? 0} orders`} accent="amber" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-2">
            <div className="text-lg font-semibold text-gray-900">Today’s Appointments</div>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white">
            <ul className="divide-y">
              {ops?.today?.length ? ops.today.map(v => (
                <li key={v.id} className="p-3 sm:p-4 flex items-center gap-3">
                  <div className="w-20 text-sm text-gray-600">{new Date(v.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Visit #{v.id}</div>
                    <div className="text-xs text-gray-500">Patient ID: {v.patient_id}{v.issue ? ` · ${v.issue}` : ''}</div>
                  </div>
                  <a href={`/visits/new?patient_id=${v.patient_id}`} className="text-sm rounded-md bg-indigo-600 text-white px-3 py-1.5 hover:bg-indigo-700">Open</a>
                </li>
              )) : (
                <li className="p-6 text-sm text-gray-500">No appointments recorded yet today.</li>
              )}
            </ul>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <div className="text-lg font-semibold text-gray-900 mb-2">Alerts</div>
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
              {lab && lab.length > 0 ? (
                <div>{lab.length} lab job(s) pending</div>
              ) : (
                <div>No pending lab jobs.</div>
              )}
            </div>
          </div>
          <div>
            <div className="text-lg font-semibold text-gray-900 mb-2">Quick Actions</div>
            <div className="grid grid-cols-2 gap-3">
              <a href="/visits/new" className="rounded-lg border border-gray-200 bg-white p-3 hover:bg-indigo-50">Start Consultation</a>
              <a href="/prescriptions" className="rounded-lg border border-gray-200 bg-white p-3 hover:bg-indigo-50">New Prescription</a>
              <a href="/patients" className="rounded-lg border border-gray-200 bg-white p-3 hover:bg-indigo-50">Find Patient</a>
              <a href="/pos" className="rounded-lg border border-gray-200 bg-white p-3 hover:bg-indigo-50">POS Checkout</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )}
}

