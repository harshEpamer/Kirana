import { useState } from 'react'

export default function CouponInput({ onApply, disabled }) {
  const [code, setCode] = useState('')

  const handleApply = () => {
    if (code.trim()) onApply(code.trim().toUpperCase())
  }

  return (
    <div className="flex gap-2">
      <input
        className="border rounded px-3 py-1.5 text-sm flex-1"
        placeholder="Enter coupon code"
        value={code}
        onChange={e => setCode(e.target.value.toUpperCase())}
        disabled={disabled}
      />
      <button
        onClick={handleApply}
        disabled={disabled || !code.trim()}
        className="bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-300 px-4 py-1.5 rounded text-sm font-medium"
      >
        Apply
      </button>
    </div>
  )
}
