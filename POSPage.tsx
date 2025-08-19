import { useState } from 'react'
import { useAuth } from './AuthContext'

type Line = { product_id: number; batch_id?: number; quantity: number; price: number; gst_rate: number; discount_rate: number }

export default function POSPage() {
  const { accessToken } = useAuth()
  const [patientId, setPatientId] = useState<number | ''>('')
  const [lines, setLines] = useState<Line[]>([])
  const [discount, setDiscount] = useState<number | ''>('')
  const [paymentCash, setPaymentCash] = useState<number | ''>('')
  const [paymentCard, setPaymentCard] = useState<number | ''>('')
  const [paymentUpi, setPaymentUpi] = useState<number | ''>('')
  const [result, setResult] = useState<any | null>(null)

  const addLine = () => setLines(prev => [...prev, { product_id: 0, quantity: 1, price: 0, gst_rate: 0, discount_rate: 0 } as Line])
  const updateLine = (i: number, patch: Partial<Line>) => setLines(prev => prev.map((ln, idx) => idx === i ? { ...ln, ...patch } : ln))
  const removeLine = (i: number) => setLines(prev => prev.filter((_, idx) => idx !== i))

  const checkout = async () => {
    const payments: any[] = []
    const addPay = (method: string, amount: number | '') => { const v = Number(amount || 0); if (v > 0) payments.push({ method, amount: v }) }
    addPay('cash', paymentCash); addPay('card', paymentCard); addPay('upi', paymentUpi)
    const payload = { patient_id: patientId || undefined, lines, payments, discount_amount: Number(discount || 0) }
    const res = await fetch('/api/pos/checkout', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` }, body: JSON.stringify(payload) })
    setResult(await res.json())
  }

  const subtotal = lines.reduce((s, l) => s + Number(l.price || 0) * Number(l.quantity || 0), 0)
  const gst = lines.reduce((s, l) => s + (Number(l.price || 0) * Number(l.quantity || 0)) * Number(l.gst_rate || 0) / 100, 0)
  const total = subtotal + gst - Number(discount || 0)

  return (
    <div className="grid gap-4">
      <div className="text-xl font-semibold">Unified POS</div>
      <div className="flex gap-2 items-center">
        <input className="border rounded p-2" placeholder="Patient ID (optional)" value={patientId} onChange={e => setPatientId(e.target.value as any)} />
        <button className="border rounded px-3" onClick={addLine}>Add Item</button>
      </div>
      <div className="grid gap-2">
        {lines.map((ln, i) => (
          <div key={i} className="border rounded p-3 grid md:grid-cols-6 gap-2">
            <input className="border rounded p-2" placeholder="Product ID" value={ln.product_id} onChange={e => updateLine(i, { product_id: Number(e.target.value || 0) })} />
            <input className="border rounded p-2" placeholder="Batch ID" value={(ln.batch_id as any) || ''} onChange={e => updateLine(i, { batch_id: e.target.value ? Number(e.target.value) : undefined })} />
            <input className="border rounded p-2" placeholder="Qty" value={ln.quantity} onChange={e => updateLine(i, { quantity: Number(e.target.value || 0) })} />
            <input className="border rounded p-2" placeholder="Price" value={ln.price} onChange={e => updateLine(i, { price: Number(e.target.value || 0) })} />
            <input className="border rounded p-2" placeholder="GST %" value={ln.gst_rate} onChange={e => updateLine(i, { gst_rate: Number(e.target.value || 0) })} />
            <button className="border rounded px-3" onClick={() => removeLine(i)}>Remove</button>
          </div>
        ))}
      </div>
      <div className="grid md:grid-cols-3 gap-2">
        <input className="border rounded p-2" placeholder="Discount" value={discount} onChange={e => setDiscount(e.target.value as any)} />
        <input className="border rounded p-2" placeholder="Cash" value={paymentCash} onChange={e => setPaymentCash(e.target.value as any)} />
        <input className="border rounded p-2" placeholder="Card" value={paymentCard} onChange={e => setPaymentCard(e.target.value as any)} />
        <input className="border rounded p-2" placeholder="UPI" value={paymentUpi} onChange={e => setPaymentUpi(e.target.value as any)} />
      </div>
      <div className="text-sm">Subtotal: {subtotal.toFixed(2)} | GST: {gst.toFixed(2)} | Total: {total.toFixed(2)}</div>
      <button className="bg-sky-600 text-white rounded py-2" onClick={checkout}>Checkout</button>
      {result && <div className="text-green-700 text-sm">Order #{result.order_id} | Total {result.total}</div>}
    </div>
  )
}

