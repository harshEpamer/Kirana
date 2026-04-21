import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getPurchaseHistory } from '../api/customersApi'

export default function PurchaseHistoryPage() {
  const { user } = useAuth()
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user?.id) return
    setLoading(true)
    getPurchaseHistory(user.id)
      .then(data => setRecords(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false))
  }, [user?.id])

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4 text-green-700">My Orders</h1>

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : records.length === 0 ? (
        <p className="text-gray-400 text-sm">No purchases yet. <a href="/catalog" className="text-green-600 underline">Start shopping</a>.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-green-50 text-left">
                <th className="border px-3 py-2">Sale #</th>
                <th className="border px-3 py-2">Date</th>
                <th className="border px-3 py-2">Final Amount</th>
              </tr>
            </thead>
            <tbody>
              {records.map(r => (
                <tr key={r.sale_id} className="hover:bg-green-50">
                  <td className="border px-3 py-2">#{r.sale_id}</td>
                  <td className="border px-3 py-2 text-xs text-gray-500">{r.sale_time?.slice(0, 16).replace('T', ' ')}</td>
                  <td className="border px-3 py-2 font-semibold text-green-700">₹{r.final_amount?.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
