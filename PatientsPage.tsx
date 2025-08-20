import { useEffect, useState } from 'react'
import { useAuth } from './AuthContext'

export default function PatientsPage() {
  const { accessToken } = useAuth()
  const [q, setQ] = useState('')
  const [rows, setRows] = useState<any[]>([])
  const [firstName, setFirst] = useState('')
  const [lastName, setLast] = useState('')
  const [phone, setPhone] = useState('')
  const [age, setAge] = useState<number | ''>('')
  const [gender, setGender] = useState('')

  const load = async (page: number = 1) => {
    const res = await fetch(`/api/patients?q=${encodeURIComponent(q)}&page=${page}&page_size=50`, { headers: { Authorization: `Bearer ${accessToken}` } })
    setRows(await res.json())
  }
  useEffect(() => { load() }, [])

  const add = async () => {
    const payload: any = { first_name: firstName.trim(), last_name: lastName.trim(), phone: phone.trim(), gender }
    if (age !== '') payload.age = Number(age)
    await fetch('/api/patients', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` }, body: JSON.stringify(payload) })
    setFirst(''); setLast(''); setPhone(''); setAge(''); setGender('')
    load()
  }

  return (
    <div className="grid gap-4">
      <div className="flex gap-2">
        <input className="border rounded p-2" placeholder="Search name/phone" value={q} onChange={e => setQ(e.target.value)} />
        <button className="border rounded px-3" onClick={load}>Search</button>
      </div>
      <div className="grid md:grid-cols-2 gap-3">
        <div className="border rounded p-3 grid gap-2">
          <div className="font-medium">Add Patient</div>
          <input className="border rounded p-2" placeholder="First name" value={firstName} onChange={e => setFirst(e.target.value)} />
          <input className="border rounded p-2" placeholder="Last name" value={lastName} onChange={e => setLast(e.target.value)} />
          <input className="border rounded p-2" placeholder="Phone" value={phone} onChange={e => setPhone(e.target.value)} />
          <div className="grid grid-cols-2 gap-2">
            <input className="border rounded p-2" placeholder="Age" value={age} onChange={e => setAge(e.target.value as any)} />
            <input className="border rounded p-2" placeholder="Gender" value={gender} onChange={e => setGender(e.target.value)} />
          </div>
          <button className="bg-sky-600 text-white rounded py-2" onClick={add}>Save</button>
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
    </div>
  )
}
