import { useEffect, useState } from 'react'
import { getLowStockAlerts } from '../api/alertsApi'
import { restockProduct } from '../api/inventoryApi'

export default function AdminAlertsPage() {
  const [alerts,  setAlerts]  = useState([])
  const [qtyMap,  setQtyMap]  = useState({}) // { productId: quantity }
  const [msg,     setMsg]     = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    getLowStockAlerts()
      .then(data => {
        const list = Array.isArray(data) ? data : []
        setAlerts(list)
        const init = {}
        list.forEach(a => { init[a.id] = a.suggested_reorder_qty || a.shortfall })
        setQtyMap(init)
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const flashMsg = (text) => {
    setMsg(text)
    setTimeout(() => setMsg(''), 2500)
  }

  const restockOne = async (productId) => {
    const qty = Number(qtyMap[productId] || 0)
    if (qty <= 0) return
    await restockProduct(productId, qty)
    flashMsg('Stock updated!')
    load()
  }

  const restockAll = async () => {
    for (const a of alerts) {
      const qty = Number(qtyMap[a.id] || 0)
      if (qty > 0) await restockProduct(a.id, qty)
    }
    flashMsg('All low-stock items restocked!')
    load()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-red-600">Low Stock Alerts</h1>
        {alerts.length > 0 && (
          <button onClick={restockAll} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm font-medium">
            Restock All
          </button>
        )}
      </div>

      {msg && <div className="bg-green-100 text-green-700 px-4 py-2 rounded mb-4 text-sm">{msg}</div>}

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : alerts.length === 0 ? (
        <div className="bg-green-50 border border-green-300 text-green-700 px-4 py-3 rounded">
          ✓ All items are well-stocked.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-red-50 text-left">
                <th className="border px-3 py-2">Product</th>
                <th className="border px-3 py-2">Category</th>
                <th className="border px-3 py-2">Current Qty</th>
                <th className="border px-3 py-2">Threshold</th>
                <th className="border px-3 py-2">Reorder Qty</th>
                <th className="border px-3 py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map(a => (
                <tr key={a.id} className="hover:bg-red-50">
                  <td className="border px-3 py-2 font-medium">{a.name}</td>
                  <td className="border px-3 py-2">{a.category}</td>
                  <td className="border px-3 py-2 text-red-600 font-semibold">{a.stock_qty}</td>
                  <td className="border px-3 py-2">{a.reorder_threshold}</td>
                  <td className="border px-3 py-2">
                    <input
                      type="number"
                      min="1"
                      className="border rounded p-1 text-sm w-20"
                      value={qtyMap[a.id] ?? ''}
                      onChange={e => setQtyMap(m => ({ ...m, [a.id]: e.target.value }))}
                    />
                  </td>
                  <td className="border px-3 py-2">
                    <button
                      onClick={() => restockOne(a.id)}
                      className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs font-medium"
                    >
                      Restock
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
