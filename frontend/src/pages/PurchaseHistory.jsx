import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { getCustomerHistory } from '../api/customersApi'

export default function PurchaseHistory() {
  const { user, token } = useAuth()
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      setLoading(false)
      return
    }
    getCustomerHistory(user.id, token)
      .then(data => {
        setRecords(Array.isArray(data) ? data : [])
      })
      .catch(() => setError('Failed to load purchase history'))
      .finally(() => setLoading(false))
  }, [user, token])

  if (!user) {
    return <p className="text-center mt-10 text-gray-400">Please login to view your purchase history.</p>
  }

  if (loading) {
    return <p className="text-center mt-10 text-gray-400">Loading...</p>
  }

  if (error) {
    return <p className="text-center mt-10 text-red-500">{error}</p>
  }

  if (records.length === 0) {
    return (
      <div className="max-w-2xl mx-auto mt-10 text-center">
        <h1 className="text-2xl font-bold mb-4 text-green-700">Purchase History</h1>
        <p className="text-gray-400">No purchases yet.</p>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6 text-green-700">Purchase History</h1>
      <div className="space-y-4">
        {records.map(r => (
          <div key={r.sale_id} className="border rounded-lg p-4 shadow-sm">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-500">
                {r.sale_time ? new Date(r.sale_time).toLocaleString() : 'N/A'}
              </span>
              <span className="text-xs text-gray-400">Order #{r.sale_id}</span>
            </div>
            <table className="w-full text-sm mb-2">
              <thead>
                <tr className="border-b text-left text-gray-600">
                  <th className="py-1">Item</th>
                  <th className="py-1 text-center">Qty</th>
                  <th className="py-1 text-right">Price</th>
                  <th className="py-1 text-right">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                {r.items.map((item, idx) => (
                  <tr key={idx} className="border-b">
                    <td className="py-1">{item.product_name}</td>
                    <td className="py-1 text-center">{item.quantity}</td>
                    <td className="py-1 text-right">₹{item.unit_price.toFixed(2)}</td>
                    <td className="py-1 text-right">₹{(item.unit_price * item.quantity).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="flex justify-end gap-4 text-sm">
              <span className="text-gray-500">Total: ₹{r.total_amount.toFixed(2)}</span>
              {r.discount_amount > 0 && (
                <span className="text-green-600">Discount: -₹{r.discount_amount.toFixed(2)}</span>
              )}
              <span className="font-bold text-green-700">Final: ₹{r.final_amount.toFixed(2)}</span>
            </div>
            {r.coupon_code && (
              <p className="text-xs text-gray-400 mt-1">Coupon: {r.coupon_code}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
