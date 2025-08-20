import React from 'react'

type Props = {
  title: string
  value: string | number
  subtitle?: string
  accent?: 'blue' | 'green' | 'indigo' | 'rose' | 'amber'
}

export default function KPICard({ title, value, subtitle, accent = 'indigo' }: Props) {
  const ring = {
    blue: 'ring-blue-100',
    green: 'ring-green-100',
    indigo: 'ring-indigo-100',
    rose: 'ring-rose-100',
    amber: 'ring-amber-100',
  }[accent]
  const dot = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    indigo: 'bg-indigo-500',
    rose: 'bg-rose-500',
    amber: 'bg-amber-500',
  }[accent]
  return (
    <div className={`rounded-xl border border-gray-200 ring-4 ${ring} p-4 bg-white`}
         style={{ boxShadow: '0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04)' }}>
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600 font-medium flex items-center gap-2">
          <span className={`inline-block w-2 h-2 rounded-full ${dot}`} />
          {title}
        </div>
      </div>
      <div className="mt-2 text-2xl font-semibold tracking-tight text-gray-900">{value}</div>
      {subtitle && <div className="mt-1 text-xs text-gray-500">{subtitle}</div>}
    </div>
  )
}


