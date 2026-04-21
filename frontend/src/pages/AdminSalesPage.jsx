import { useEffect, useState, useMemo } from 'react'
import { listSales } from '../api/salesApi'

const todayISO = () => new Date().toISOString().slice(0, 10)

export default function AdminSalesPage() {
  const [sales,   setSales]   = useState([])
  const [date,    setDate]    = useState(todayISO())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    listSales()
      .then(data => setSales(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(
    () => sales.filter(s => s.sale_time?.startsWith(date)),
    [sales, date]
  )

  const summary = useMemo(() => {
    const revenue = filtered.reduce((s, r) => s + (r.final_amount || 0), 0)
    const orders  = filtered.length
    // Top product
    const counts = {}
    filtered.forEach(s => (s.items || []).forEach(it => {
      counts[it.product_id] = (counts[it.product_id] || 0) + it.quantity
    }))
    let topId = null, topQty = 0
    for (const [pid, q] of Object.entries(counts)) {
      if (q > topQty) { topQty = q; topId = pid }
    }
    return { revenue, orders, topId, topQty }
  }, [filtered])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-green-700">Sales Report</h1>

      <div className="mb-6 flex items-center gap-3">
        <label className="text-sm text-gray-600">Date:</label>
        <input
          type="date"
          value={date}
          onChange={e => setDate(e.target.value)}
          className="border rounded px-3 py-1.5 text-sm"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-green-50 border border-green-200 rounded p-4">
          <div className="text-xs text-gray-500 uppercase">Revenue</div>
          <div className="text-2xl font-bold text-green-700">₹{summary.revenue.toFixed(2)}</div>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded p-4">
          <div className="text-xs text-gray-500 uppercase">Orders</div>
          <div className="text-2xl font-bold text-blue-700">{summary.orders}</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <div className="text-xs text-gray-500 uppercase">Top Product</div>
          <div className="text-2xl font-bold text-yellow-700">
            {summary.topId ? `#${summary.topId}` : '—'}
            {summary.topQty > 0 && <span className="text-sm font-normal ml-2">×{summary.topQty}</span>}
          </div>
        </div>
      </div>

      <h2 className="text-lg font-semibold mb-3 text-gray-700">Transactions on {date}</h2>

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : filtered.length === 0 ? (
        <p className="text-gray-400 text-sm">No sales recorded for this date.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-green-50 text-left">
                <th className="border px-3 py-2">Time</th>
                <th className="border px-3 py-2">Sale #</th>
                <th className="border px-3 py-2">User</th>
                <th className="border px-3 py-2">Items</th>
                <th className="border px-3 py-2">Total</th>
                <th className="border px-3 py-2">Discount</th>
                <th className="border px-3 py-2">Final</th>
                <th className="border px-3 py-2">Coupon</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(s => (
                <tr key={s.id} className="hover:bg-green-50">
                  <td className="border px-3 py-2 text-xs text-gray-500">{s.sale_time?.slice(11, 16)}</td>
                  <td className="border px-3 py-2">#{s.id}</td>
                  <td className="border px-3 py-2">{s.user_id}</td>
                  <td className="border px-3 py-2 text-xs">{(s.items || []).length} items</td>
                  <td className="border px-3 py-2">₹{s.total_amount?.toFixed(2)}</td>
                  <td className="border px-3 py-2 text-orange-600">-₹{s.discount_amount?.toFixed(2)}</td>
                  <td className="border px-3 py-2 font-semibold text-green-700">₹{s.final_amount?.toFixed(2)}</td>
                  <td className="border px-3 py-2 text-xs">{s.coupon_code || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
