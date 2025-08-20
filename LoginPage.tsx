import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function LoginPage() {
  const [email, setEmail] = useState('doctor@maueyecare.com')
  const [password, setPassword] = useState('')
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
    const res = await fetch('/api/auth/login', { method: 'POST', body: form, headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
    if (!res.ok) { setError('Invalid credentials'); return }
    const data = await res.json()
    login(data.access_token, data.refresh_token)
    nav('/')
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

