import { useState, useEffect } from 'react'
import { getLowStockAlerts } from '../api/alertsApi'
import { listSales } from '../api/salesApi'

export default function AdminDashboard() {
  const [alerts, setAlerts] = useState([])
  const [sales,  setSales]  = useState([])

  useEffect(() => {
    getLowStockAlerts().then(setAlerts)
    listSales().then(setSales)
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-green-700">Admin Dashboard</h1>

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3 text-red-600">
          Low Stock Alerts ({alerts.length})
        </h2>
        {alerts.length === 0 ? (
          <p className="text-gray-400 text-sm">All products are well stocked.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-red-50 text-left">
                  <th className="border px-3 py-2">Product</th>
                  <th className="border px-3 py-2">Category</th>
                  <th className="border px-3 py-2">Stock</th>
                  <th className="border px-3 py-2">Threshold</th>
                  <th className="border px-3 py-2">Shortfall</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map(a => (
                  <tr key={a.id} className="hover:bg-red-50">
                    <td className="border px-3 py-2">{a.name}</td>
                    <td className="border px-3 py-2">{a.category}</td>
                    <td className="border px-3 py-2 text-red-600 font-semibold">{a.stock_qty}</td>
                    <td className="border px-3 py-2">{a.reorder_threshold}</td>
                    <td className="border px-3 py-2 text-orange-600">{a.shortfall}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3 text-green-700">Recent Sales</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-green-50 text-left">
                <th className="border px-3 py-2">Sale #</th>
                <th className="border px-3 py-2">Total</th>
                <th className="border px-3 py-2">Discount</th>
                <th className="border px-3 py-2">Final</th>
                <th className="border px-3 py-2">Coupon</th>
                <th className="border px-3 py-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {sales.slice(0, 20).map(s => (
                <tr key={s.id} className="hover:bg-green-50">
                  <td className="border px-3 py-2">{s.id}</td>
                  <td className="border px-3 py-2">₹{s.total_amount?.toFixed(2)}</td>
                  <td className="border px-3 py-2">₹{s.discount_amount?.toFixed(2)}</td>
                  <td className="border px-3 py-2 font-semibold">₹{s.final_amount?.toFixed(2)}</td>
                  <td className="border px-3 py-2">{s.coupon_code || '—'}</td>
                  <td className="border px-3 py-2 text-xs text-gray-400">{s.sale_time?.slice(0, 16)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
