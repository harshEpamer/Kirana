import { useState } from 'react'
import { validateCoupon } from '../api/couponsApi'

/**
 * Reusable coupon input. Calls parent with discount info when applied.
 * Props:
 *   orderTotal    — current cart subtotal
 *   onApplied({ code, amount })  — called on successful validation
 *   onRemoved()                   — called when user clears coupon
 */
export default function CouponInput({ orderTotal, onApplied, onRemoved }) {
  const [code, setCode]       = useState('')
  const [applied, setApplied] = useState(null)
  const [error, setError]     = useState('')
  const [busy, setBusy]       = useState(false)

  const apply = async () => {
    if (!code.trim()) return
    setBusy(true); setError('')
    try {
      const res = await validateCoupon({ code: code.trim().toUpperCase(), order_total: orderTotal })
      if (res.valid) {
        setApplied({ code: code.trim().toUpperCase(), amount: res.discount_amount })
        setError('')
        onApplied?.({ code: code.trim().toUpperCase(), amount: res.discount_amount })
      } else {
        setError(res.message || 'Invalid coupon')
        setApplied(null)
        onRemoved?.()
      }
    } catch {
      setError('Could not validate coupon')
    } finally {
      setBusy(false)
    }
  }

  const remove = () => {
    setApplied(null)
    setCode('')
    setError('')
    onRemoved?.()
  }

  if (applied) {
    return (
      <div className="flex items-center justify-between bg-green-50 border border-green-300 rounded px-3 py-2">
        <span className="text-sm text-green-700 font-medium">
          ✓ {applied.code} applied — ₹{applied.amount.toFixed(2)} off
        </span>
        <button onClick={remove} className="text-xs text-red-500 hover:underline">Remove</button>
      </div>
    )
  }

  return (
    <div>
      <div className="flex gap-2">
        <input
          className="border rounded px-3 py-1.5 text-sm flex-1"
          placeholder="Coupon code (e.g. SAVE10)"
          value={code}
          onChange={e => setCode(e.target.value.toUpperCase())}
          disabled={busy}
        />
        <button
          onClick={apply}
          disabled={busy || !code.trim()}
          className="bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-300 px-4 py-1.5 rounded text-sm font-medium"
        >
          {busy ? 'Checking…' : 'Apply'}
        </button>
      </div>
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  )
}
