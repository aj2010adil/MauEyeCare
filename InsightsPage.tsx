import { useEffect, useState } from 'react'
import { useAuth } from './AuthContext'

export default function InsightsPage() {
  const { accessToken } = useAuth()
  const [ideas, setIdeas] = useState<string[]>([])
  useEffect(() => {
    fetch('/api/insights/suggestions', { headers: { Authorization: `Bearer ${accessToken}` } })
      .then(r => r.json()).then(d => setIdeas(d.suggestions || [])).catch(() => setIdeas([]))
  }, [accessToken])
  return (
    <div className="grid gap-3">
      <div className="text-xl font-semibold">Suggest new ideas</div>
      <ul className="list-disc pl-5">
        {ideas.map((s, i) => <li key={i}>{s}</li>)}
      </ul>
    </div>
  )
}

