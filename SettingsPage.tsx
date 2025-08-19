import { useState } from 'react'

export default function SettingsPage() {
  const [status, setStatus] = useState('')
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
      <div className="text-sm">Prescriptions will be saved under %USERPROFILE%\Documents\MauEyeCare\prescriptions\YYYY\MM-DD\</div>
    </div>
  )
}
