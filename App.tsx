import { Routes, Route, Link, Outlet, useNavigate } from 'react-router-dom'
import { createContext, useContext, useEffect, useState } from 'react'
import jwtDecode from 'jwt-decode'

function useAuthProvider() {
  const [accessToken, setAccessToken] = useState<string | null>(localStorage.getItem('access'))
  const [refreshToken, setRefreshToken] = useState<string | null>(localStorage.getItem('refresh'))

  const login = (access: string, refresh: string) => {
    setAccessToken(access)
    setRefreshToken(refresh)
    localStorage.setItem('access', access)
    localStorage.setItem('refresh', refresh)
  }
  const logout = () => {
    setAccessToken(null)
    setRefreshToken(null)
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
  }
  return { accessToken, refreshToken, login, logout }
}

type AuthContextType = ReturnType<typeof useAuthProvider>
const AuthContext = createContext<AuthContextType | null>(null)
export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside provider')
  return ctx
}

function AuthProvider({ children }: { children: React.ReactNode }) {
  const value = useAuthProvider()
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { accessToken } = useAuth()
  const navigate = useNavigate()
  useEffect(() => {
    if (!accessToken) navigate('/login')
  }, [accessToken])
  return <>{children}</>
}

function Layout() {
  const { logout } = useAuth()
  return (
    <div className="min-h-screen grid grid-rows-[auto,1fr]">
      <header className="border-b p-3 flex gap-4 items-center">
        <div className="font-semibold">MauEyeCare</div>
        <nav className="flex gap-3 text-sm">
          <Link to="/">Dashboard</Link>
          <Link to="/patients">Patients</Link>
          <Link to="/visits/new">New Visit</Link>
          <Link to="/settings">Settings</Link>
        </nav>
        <div className="ml-auto">
          <button className="text-sm" onClick={logout}>Logout</button>
        </div>
      </header>
      <main className="p-4"><Outlet /></main>
    </div>
  )
}

function Dashboard() {
  const [data, setData] = useState<any | null>(null)
  const { accessToken } = useAuth()
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

function LoginPage() {
  const [email, setEmail] = useState('doctor@maueyecare.com')
  const [password, setPassword] = useState('changeme')
  const [error, setError] = useState<string | null>(null)
  const { login } = useAuth()
  const nav = useNavigate()
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    const form = new URLSearchParams()
    form.set('username', email)
    form.set('password', password)
    form.set('grant_type', 'password')
    try {
      const res = await fetch('/api/auth/login', { method: 'POST', body: form, headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
      if (!res.ok) throw new Error('Login failed')
      const data = await res.json()
      login(data.access_token, data.refresh_token)
      nav('/')
    } catch (e: any) {
      setError(e.message)
    }
  }
  return (
    <div className="min-h-screen grid place-items-center">
      <form onSubmit={submit} className="w-80 border rounded p-4 grid gap-3">
        <div className="text-lg font-semibold">Login</div>
        <input className="border rounded p-2" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input className="border rounded p-2" placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <button className="bg-sky-600 text-white rounded py-2">Sign in</button>
      </form>
    </div>
  )
}

function PatientsPage() {
  const { accessToken } = useAuth()
  const [q, setQ] = useState('')
  const [rows, setRows] = useState<any[]>([])
  const load = async () => {
    const res = await fetch('/api/patients?q=' + encodeURIComponent(q), { headers: { Authorization: `Bearer ${accessToken}` } })
    setRows(await res.json())
  }
  useEffect(() => { load() }, [])
  return (
    <div className="grid gap-3">
      <div className="flex gap-2">
        <input className="border rounded p-2" placeholder="Search name/phone" value={q} onChange={e => setQ(e.target.value)} />
        <button className="border rounded px-3" onClick={load}>Search</button>
      </div>
      <div className="grid gap-2">
        {rows.map(r => (
          <div key={r.id} className="border rounded p-3 flex gap-3">
            <div className="font-medium">{r.first_name} {r.last_name}</div>
            <div className="text-sm text-gray-500">{r.phone}</div>
            <div className="ml-auto text-sm">{r.gender} {r.age ? `• ${r.age}` : ''}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function NewVisitPage() {
  const { accessToken } = useAuth()
  const [patientId, setPatientId] = useState<number>(0)
  const [issue, setIssue] = useState('')
  const [advice, setAdvice] = useState('')
  const save = async () => {
    const res = await fetch('/api/visits', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` }, body: JSON.stringify({ patient_id: patientId, issue, advice }) })
    if (res.ok) { setIssue(''); setAdvice('') }
  }
  return (
    <div className="grid gap-3 max-w-xl">
      <div className="text-xl font-semibold">New Visit</div>
      <input className="border rounded p-2" placeholder="Patient ID" type="number" value={patientId} onChange={e => setPatientId(parseInt(e.target.value || '0'))} />
      <input className="border rounded p-2" placeholder="Issue" value={issue} onChange={e => setIssue(e.target.value)} />
      <input className="border rounded p-2" placeholder="Advice" value={advice} onChange={e => setAdvice(e.target.value)} />
      <button className="bg-sky-600 text-white rounded py-2" onClick={save}>Save Visit</button>
    </div>
  )
}

function SettingsPage() {
  const { accessToken } = useAuth()
  const [status, setStatus] = useState<string>('')
  const bootstrap = async () => {
    const res = await fetch('/api/auth/bootstrap', { method: 'POST' })
    const data = await res.json()
    setStatus(data.created ? 'Created default doctor' : 'Already present')
  }
  return (
    <div className="grid gap-3">
      <div className="text-xl font-semibold">Settings</div>
      <button className="border rounded px-3 py-2" onClick={bootstrap}>Ensure Default Doctor</button>
      <div className="text-sm text-gray-500">{status}</div>
      <div className="text-sm">Prescriptions save path follows: %USERPROFILE%\Documents\MauEyeCare\prescriptions\YYYY\MM-DD\</div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<AuthGuard><Layout /></AuthGuard>}>
          <Route index element={<Dashboard />} />
          <Route path="patients" element={<PatientsPage />} />
          <Route path="visits/new" element={<NewVisitPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App