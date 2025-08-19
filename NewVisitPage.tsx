import { useState } from 'react'
import { useAuth } from './AuthContext'

export default function NewVisitPage() {
  const { accessToken } = useAuth()
  const [patientId, setPatientId] = useState<number>(0)
  const [issue, setIssue] = useState('')
  const [advice, setAdvice] = useState('')
  const [saved, setSaved] = useState(false)

  const save = async () => {
    setSaved(false)
    const res = await fetch('/api/visits', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` }, body: JSON.stringify({ patient_id: patientId, issue, advice }) })
    if (res.ok) { setIssue(''); setAdvice(''); setSaved(true) }
  }

  return (
    <div className="grid gap-3 max-w-xl">
      <div className="text-xl font-semibold">New Visit</div>
      <input className="border rounded p-2" placeholder="Patient ID" type="number" value={patientId} onChange={e => setPatientId(parseInt(e.target.value || '0'))} />
      <input className="border rounded p-2" placeholder="Issue" value={issue} onChange={e => setIssue(e.target.value)} />
      <input className="border rounded p-2" placeholder="Advice" value={advice} onChange={e => setAdvice(e.target.value)} />
      <button className="bg-sky-600 text-white rounded py-2" onClick={save}>Save Visit</button>
      {saved && <div className="text-green-700 text-sm">Saved.</div>}
    </div>
  )
}
